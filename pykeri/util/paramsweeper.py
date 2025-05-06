# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 16:11:28 2017

ParamSweeper generates databases of tasks, and sweeps them to solve the tasks.
    It manages the parameters for parallel computation.

@author: Jaywan Chung

updated on April 04 2018: causes error when there is no 'param' and only 'const'.
updated on April 04 2018: bug fix of "generate()" function; error caused when there is only ONE task.
"""

import sqlite3
from math import ceil
from pykeri.util.timer import Timer
from pykeri.util.sqlite_util import DB_create_columns_if_not_exists, \
    DB_has_a_column, DB_create_a_column_if_not_exists

class ParamSweeper:
    """
    Warning: if there is no 'param' (only 'const'), the function "generate()" does NOT work!
    """
    
    TBL_PROGRESS = "param_progress"
    COL_PARAM = "param"
    COL_TYPE = "type"
    TYPE_RANGE = "range"
    TYPE_LIST = "list"
    COL_START_VALUE = "start_value"
    COL_END_VALUE = "end_value"
    COL_MIN_VALUE = "minimum_value"
    COL_MAX_VALUE = "maximum_value"
    COL_CUR_VALUE = "current_value"
    TBL_CONST = "constant"
    COL_CONST = "name"
    COL_VALUE = "value"
    TBL_PARAM_INFO = "param_info"
    COL_INFO = "info"
    TBL_SWEEP_INFO = "sweep_info"
    COL_OPTION = "option"
    
    TBL_RESULT = "result"
    
    COMMIT_INTERVAL = "commit_interval"
    
    def __init__(self,filename=None):
        self._list_param = []
        self._dict_param = {}
        self._dict_param_by_list = {}
        self._list_const = []
        self._dict_const = {}
        self._start_indices = None
        self._end_indices = None
        self._current_indices = None
        self._filename = None

        self._dict_sweep_info = {self.COMMIT_INTERVAL:60}  # default is one minute (60 seconds)
        self.solver = ParamSweeper._null_solver
                
        if filename is None:
            pass
        else:
            self.load(filename)

    def sweep(self,quiet=True):
        # prepare the iterator
        if self._current_indices:
            start_indices = self._current_indices   # continue the progress
        else:
            start_indices = self._start_indices        
        it = SweepIndexIterator(start_indices, self._end_indices, self._largest_indices())
        if self._current_indices:
            next(it)    # the current progress means it has been done. so do the next job.
        # open the DB
        con = sqlite3.connect(self._filename)
        cur = con.cursor()
        # sweep
        timer = Timer()
        commit_interval = self._dict_sweep_info[self.COMMIT_INTERVAL]
        checked_columns = False; columns_str = ''
        result_tbl = self.TBL_RESULT
        for indices in it:
            # create input and output
            input_dict, output_dict = self._indices_to_input_and_output(indices)
            # print to the console
            if not quiet:
                print("COMPUTED:")
                ParamSweeper._print_input_and_output(input_dict,output_dict)
            # check the columns once
            if not checked_columns:
                input_keys = tuple(input_dict.keys())
                output_keys = tuple(output_dict.keys())
                columns = input_keys + output_keys  # input and output params
                #print(columns)
                # create the result table if not exists
                columns_str = ''.join([col+',' for col in columns[:-1]]) + columns[-1]
                columns_and_types_str = ''.join([col+' REAL,' for col in columns[:-1]]) + columns[-1]+' REAL'
                cur.execute("CREATE TABLE IF NOT EXISTS "+result_tbl+"("+columns_and_types_str+")")
                DB_create_columns_if_not_exists(cur,columns,result_tbl)  # REAL columns
                checked_columns = True
                # check the current value entry
                DB_create_a_column_if_not_exists(cur,self.COL_CUR_VALUE,self.TBL_PROGRESS)
            # insert new results
            input_values = tuple(input_dict.values())
            output_values = tuple(output_dict.values())
            results = input_values + output_values  # input and output values
            results_str = ''.join([str(value)+',' for value in results[:-1]]) + str(results[-1])
            cur.execute("INSERT INTO "+result_tbl+"("+columns_str+")"+" VALUES ("+results_str+")")
            # update the current values
            for input_key,input_value in zip(input_keys,input_values):
                cur.execute( "UPDATE "+self.TBL_PROGRESS+" SET "+self.COL_CUR_VALUE+"="+str(input_value)+" WHERE "+self.COL_PARAM+"='"+input_key+"'" )
            # commit the DB
            if timer.elapsed(commit_interval):
                con.commit()
                timer.restart()
                if not quiet:
                    print("DB recorded.")
        con.commit()
        con.close()
            
    def _indices_to_input_and_output(self,indices):
        values = self._indices_to_values(indices)
        param_dict = {param:value for param,value in zip(self._list_param,values)}
        const_dict = self._dict_const
        input_dict = {**param_dict, **const_dict}     # Python 3.5 or above only: merge two dictionaries
        output_dict = self.solver(input_dict)
        return input_dict, output_dict
    
    def _print_input_and_output(input_dict,output_dict):
        print("input = ", input_dict, ":")
        for key,val in output_dict.items():
            print("  ", key, "=", val)
        
    def load(self,filename):
        self._filename = filename

        con = sqlite3.connect(filename)
        cur = con.cursor()
        
        self._load_progress_and_info_table(cur)
        self._load_const_table(cur)
        self._load_sweep_info(cur)
        
        con.commit()
        con.close()
    
    def generate(self,filename_header,num_DB):
        if len(self._list_param) == 0:  # Error Handling: Apr 04 2018
            raise ValueError("There is no parameter. A sweeper with only constants is not allowed.")
        
        start_indices = tuple( [0]*len(self._list_param) )
        end_indices = self._largest_indices()
        largest_indices = self._largest_indices()
        
        order_start_indices = indices_to_order(start_indices,largest_indices)
        order_end_indices = indices_to_order(end_indices,largest_indices)
        num_tasks = order_end_indices - order_start_indices + 1
        avg_tasks_per_DB = ceil(num_tasks/num_DB)
        
        start_orders = list(range(order_start_indices,order_end_indices,avg_tasks_per_DB))
        if len(start_orders) == 0:  # bug fix for empty list on April 04 2018
            start_orders = [0]
        end_orders = [order-1 for order in start_orders[1:]] + [order_end_indices]
        
        for i in range(num_DB):
            postfix = str(i+1)
            DB_start_indices = order_to_indices(start_orders[i],largest_indices)
            DB_end_indices = order_to_indices(end_orders[i],largest_indices)
            self._generate_a_DB(filename_header+postfix+".db",DB_start_indices,DB_end_indices)
        print("Total", num_DB, "DB(s) generated; each has approximately", avg_tasks_per_DB, "tasks.")

    def _generate_a_DB(self,filename,start_indices,end_indices):
        con = sqlite3.connect(filename)
        cur = con.cursor()
        
        self._record_new_progress_table(cur,start_indices,end_indices)
        self._record_const_table(cur)
        self._record_param_info(cur)
        self._record_sweep_info(cur)
        
        con.commit()
        con.close()
    
    def _largest_indices(self):
        result = []
        for name in self._list_param:
            if name in self._dict_param:
                start_val, end_val, increment = self._dict_param[name]                
                index = int((end_val-start_val)/increment)
            else:
                index = len(self._dict_param_by_list[name])-1
            result.append(index)
        return tuple(result)
    
    def _record_new_progress_table(self,cur,start_indices,end_indices):
        TBL = self.TBL_PROGRESS
        PARAM = self.COL_PARAM
        TYPE = self.COL_TYPE
        START = self.COL_START_VALUE
        END = self.COL_END_VALUE
        MIN = self.COL_MIN_VALUE
        MAX = self.COL_MAX_VALUE
        cur.execute("DROP TABLE IF EXISTS "+TBL)
        cur.execute("CREATE TABLE {}({} TEXT, {} TEXT, {} REAL, {} REAL, {} REAL, {} REAL);".format(TBL,PARAM,TYPE,START,END,MIN,MAX))
        params = self._list_param
        types = []
        for param in params:
            if param in self._dict_param:
                types.append(self.TYPE_RANGE)
            else:
                types.append(self.TYPE_LIST)                
        start_values = self._indices_to_values(start_indices)
        end_values = self._indices_to_values(end_indices)
        min_values = self._indices_to_values([0]*len(params))
        max_values = self._indices_to_values(self._largest_indices())
        cur.executemany("INSERT INTO "+TBL+" VALUES(?,?,?,?,?,?);",zip(params,types,start_values,end_values,min_values,max_values))

    def _load_progress_and_info_table(self,cur):
        TBL = self.TBL_PROGRESS
        PARAM = self.COL_PARAM
        TYPE = self.COL_TYPE
        START = self.COL_START_VALUE
        END = self.COL_END_VALUE
        MIN = self.COL_MIN_VALUE
        MAX = self.COL_MAX_VALUE
        CURRENT = self.COL_CUR_VALUE
        # clear all the parameters
        self._list_param = []
        self._dict_param = {}
        self._dict_param_by_list = {}
        self._start_indices = None
        self._end_indices = None
        # restore the parameters and their infos
        cur.execute("SELECT " + "{},{},{},{},{},{}".format(PARAM,TYPE,START,END,MIN,MAX) +" FROM "+TBL)
        all_info = cur.fetchall()
        start_values = []
        end_values = []
        for param,param_type,start,end,min_val,max_val in all_info:
            self._list_param.append(param)
            cur.execute("SELECT "+self.COL_INFO+" FROM "+self.TBL_PARAM_INFO+" WHERE "+self.COL_PARAM+"='"+param+"';")
            selected = cur.fetchall()
            if param_type == self.TYPE_RANGE:
                incr = selected[0][0]
                self._dict_param[param] = (min_val,max_val,incr)
            else:
                value_list = [row[0] for row in selected]
                self._dict_param_by_list[param] = tuple(value_list)
            start_values.append(start)
            end_values.append(end)
        self._start_indices = self._values_to_indices(start_values)
        self._end_indices = self._values_to_indices(end_values)
        # recover the CURRENT column if exists
        CURRENT = self.COL_CUR_VALUE
        if DB_has_a_column(cur,CURRENT,TBL):
            cur.execute("SELECT "+CURRENT+" FROM "+TBL+";")
            current_values = [row[0] for row in cur.fetchall()]
            self._current_indices = self._values_to_indices(current_values)
        
    def _record_const_table(self,cur):
        TBL = self.TBL_CONST
        CONST = self.COL_CONST
        VALUE = self.COL_VALUE
        cur.execute("DROP TABLE IF EXISTS "+TBL)
        cur.execute("CREATE TABLE "+TBL+"("+CONST+" TEXT, "+VALUE+" REAL);")
        names = self._dict_const.keys()
        values = self._dict_const.values()
        cur.executemany("INSERT INTO "+TBL+" VALUES(?,?);",zip(names,values))
        
    def _load_const_table(self,cur):
        self._list_const = []
        self._dict_const = {}
        # restore the constants
        cur.execute("SELECT "+"{},{}".format(self.COL_CONST,self.COL_VALUE)+" FROM "+self.TBL_CONST)
        all_info = cur.fetchall()
        for const,value in all_info:
            self._list_const.append(const)
            self._dict_const[const] = value

    def _record_param_info(self,cur):
        TBL = self.TBL_PARAM_INFO
        PARAM = self.COL_PARAM
        INFO = self.COL_INFO
        cur.execute("DROP TABLE IF EXISTS "+TBL)
        cur.execute("CREATE TABLE "+TBL+"("+PARAM+" TEXT, "+INFO+" REAL);")
        # record the range type parameters
        params = self._dict_param.keys()
        incr_infos = [incr for start,end,incr in self._dict_param.values()]
        cur.executemany("INSERT INTO "+TBL+" VALUES(?,?);",zip(params,incr_infos))
        # record the list type parameters
        for param in self._dict_param_by_list:
            list_infos = self._dict_param_by_list[param]
            params = [param]*len(list_infos)
            cur.executemany("INSERT INTO "+TBL+" VALUES(?,?);",zip(params,list_infos))
            
    def _record_sweep_info(self,cur):
        TBL = self.TBL_SWEEP_INFO
        OPTION = self.COL_OPTION
        INFO = self.COL_INFO
        cur.execute("DROP TABLE IF EXISTS "+TBL)
        cur.execute("CREATE TABLE "+TBL+"("+OPTION+" TEXT, "+INFO+" REAL);")
        options = self._dict_sweep_info.keys()
        infos = self._dict_sweep_info.values()
        cur.executemany("INSERT INTO "+TBL+" VALUES(?,?);",zip(options,infos))
        
    def _load_sweep_info(self,cur):
        self._dict_sweep_info = {}
        # restore the constants
        cur.execute("SELECT "+"{},{}".format(self.COL_OPTION,self.COL_INFO)+" FROM "+self.TBL_SWEEP_INFO)
        all_info = cur.fetchall()
        for option,info in all_info:
            self._dict_sweep_info[option] = info

    def const(self,name,val):
        if name not in self._list_const:
            self._list_const.append(name)
        self._dict_const[name] = val

    def param(self,name,start_val,end_val,increment=1):
        if name not in self._list_param:
            self._list_param.append(name)
        self._dict_param[name] = (start_val,end_val,increment)
    
    def param_by_list(self,name,list_of_values):
        if name not in self._list_param:
            self._list_param.append(name)
        self._dict_param_by_list[name] = tuple( sorted(set(list_of_values)) )  # erase the redundancies

    def commit_interval(self,seconds):
        self._dict_sweep_info[self.COMMIT_INTERVAL] = seconds
        
    def max_num_items_per_db(self,num):
        self._max_num_items_per_db = num
        
    def _index_to_value(self,name,index):
        if name in self._dict_param:
            start_val, end_val, increment = self._dict_param[name]
            value = start_val + increment*index
            if value > end_val:
                raise IndexError("parameter index out of range")
            return value
        else:
            return self._dict_param_by_list[name][index]
        
    def _indices_to_values(self,indices):
        return tuple((self._index_to_value(name,index) for name,index in zip(self._list_param,indices)))
        
    def _value_to_index(self,name,value):
        if name in self._dict_param:
            start_val, end_val, increment = self._dict_param[name]
            index = (value-start_val)/increment
            if float(index).is_integer():
                return int(index)
            else:
                raise ValueError("wrong value: no index found")
        else:
            return self._dict_param_by_list[name].index(value)

    def _values_to_indices(self,values):
        return tuple((self._value_to_index(name,value) for name,value in zip(self._list_param,values)))
    
    def info(self):
        # write all the info of the current sweeper
        print(len(self._list_param), "Parameter(s):")
        for param in self._list_param:
            if param in self._dict_param:
                start_val, end_val, increment = self._dict_param[param]
                print("   {} = range(start={}, end={}, incr={})".format(param,str(start_val),str(end_val),str(increment)))
            else:
                print("   {} = list{}".format(param,str(self._dict_param_by_list[param])))
                
        print(len(self._list_const), "Constant(s):")
        for const in self._list_const:
            print("  ", const, "=", self._dict_const[const])
            
        print("Sweep Infos:")
        for option,info in self._dict_sweep_info.items():
            print("  ", option, "=", info)
            
        print("Progress:")
        if self._start_indices:
            print("  start values =", self._indices_to_values(self._start_indices))
        else:
            print("  start values = not given")
        if self._end_indices:
            print("  end values =", self._indices_to_values(self._end_indices))
        else:
            print("  end values = not given")
        if self._current_indices:
            print("  current values =", self._indices_to_values(self._current_indices))
        else:
            print("  current values = not given")
        
    def _null_solver(dict_input):
        raise AttributeError("Define a solver, which has a input argument\
                                 of parameters and output the results as dictionaries.")


class SweepIndexIterator:
    def __init__(self,start_indices,end_indices,largest_indices):
        assert( (len(start_indices)==len(end_indices)) and (len(start_indices)==len(largest_indices)) )
        self._current = start_indices
        self._end = end_indices
        self._largest = largest_indices
        
    def __iter__(self):
        return self
    
    def __next__(self):
        result = self._current
        if (result > self._end) or (result > self._largest):
            raise StopIteration
        else:
            self._current = self.next_of(self._current)
            return result

    def next_of(self,tuple_of_indices):
        result = list(tuple_of_indices)
        for pos,item in reversed(list(enumerate(tuple_of_indices))):
            if item+1 <= self._largest[pos]:
                result[pos] = item+1
                break
            else:
                if pos==0:
                    result[pos] +=1  # this will raise StopIteration in __next__()
                else:
                    result[pos] = 0
        return tuple(result)
    
    def current(self):
        return self._current


def indices_to_order(indices, largest_indices):
    # (0,0,..,0) has 0th order
    order = indices[0]
    for i,l in zip(indices[1:],largest_indices[1:]):
        order = order*(l+1)+i
    return order

def order_to_indices(order, largest_indices):
    # (0,0,..,0) has 0th order
    quotient = order
    indices = []
    for l in reversed(largest_indices[1:]):
        indices.append(quotient % (l+1))  # add the remainder
        quotient = int(quotient / (l+1))   # quotient
    indices.append(quotient)
    indices.reverse()
    return tuple(indices)
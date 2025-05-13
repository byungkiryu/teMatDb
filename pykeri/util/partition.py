# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:56:35 2017

@author: Jaywan Chung

updated on Fri Mar 09 2018: added "get_num_stages" function. added doctest.
"""

def generate_fixed_num_stages(num_elems, num_stages):
    """
    Generate all the tuples having the fixed number of stages. Each element of the tuple can have number from 0 to "num_elem"-1.
    For the definition of a "stage", see "get_num_stages" function.
    >>> for item in generate_fixed_num_stages(3, 4): print(item)
    (0, 1, 0, 1)
    (0, 1, 0, 2)
    (0, 1, 2, 0)
    (0, 1, 2, 1)
    (0, 2, 0, 1)
    (0, 2, 0, 2)
    (0, 2, 1, 0)
    (0, 2, 1, 2)
    (1, 0, 1, 0)
    (1, 0, 1, 2)
    (1, 0, 2, 0)
    (1, 0, 2, 1)
    (1, 2, 0, 1)
    (1, 2, 0, 2)
    (1, 2, 1, 0)
    (1, 2, 1, 2)
    (2, 0, 1, 0)
    (2, 0, 1, 2)
    (2, 0, 2, 0)
    (2, 0, 2, 1)
    (2, 1, 0, 1)
    (2, 1, 0, 2)
    (2, 1, 2, 0)
    (2, 1, 2, 1)
    """
    
    yield from add_stage((), num_elems, num_stages)

def add_stage(stage, num_elems, remaining_num_stages=0, prev_elem=None):
    if remaining_num_stages > 0:
        for elem in range(num_elems):
            if elem != prev_elem:
                yield from add_stage(stage + (elem,), num_elems, remaining_num_stages=remaining_num_stages-1, prev_elem=elem)
    else:
        yield stage

def get_stage_elems_and_lengths(iterable):
    """
    Return the list of the elements and the lengths for each stage of the iterable.
    For the definition of a "stage", see "get_num_stages" function.
    
    >>> get_stage_elems_and_lengths(['a','a','a','a'])
    (['a'], [4])
    >>> get_stage_elems_and_lengths(['b','b','a','a'])
    (['b', 'a'], [2, 2])
    >>> get_stage_elems_and_lengths(['a','b','c','a'])
    (['a', 'b', 'c', 'a'], [1, 1, 1, 1])
    """
    elems = []
    lengths = []
    stage_elem = iterable[0]
    length = 1
    for elem in iterable[1:]:
        #print(elem, stage_elem)
        if elem != stage_elem:   # new stage found
            elems.append(stage_elem)  # save info of old stage
            lengths.append(length)
            stage_elem = elem
            length = 1
        else:
            length += 1
    elems.append(stage_elem)
    lengths.append(length)
    return elems, lengths


def get_num_stages(iterable):
    """
    Return the number of stages. A "stage" consists of a consecutive elements of the same symbol.
    >>> get_num_stages(['a','a','a','a'])
    1
    >>> get_num_stages(['b','b','a','a'])
    2
    >>> get_num_stages(['a','b','c','a'])
    4
    """
    count = 1
    for next_elem, prev_elem in zip(iterable[1:], iterable[:-1]):
        if next_elem != prev_elem:
            count += 1
    return count


def number_partition( natural_number, number_of_partitions, min_number=0 ):
    """
    Generator for the number paritition;
    the given "natural_number" is dividied into "number_of_partitions".
    Also the minimum number in each partition "min_number" is considered.
    
    >>> for partition in number_partition(5, 3): print(partition)
    (0, 0, 5)
    (0, 1, 4)
    (0, 2, 3)
    (0, 3, 2)
    (0, 4, 1)
    (0, 5, 0)
    (1, 0, 4)
    (1, 1, 3)
    (1, 2, 2)
    (1, 3, 1)
    (1, 4, 0)
    (2, 0, 3)
    (2, 1, 2)
    (2, 2, 1)
    (2, 3, 0)
    (3, 0, 2)
    (3, 1, 1)
    (3, 2, 0)
    (4, 0, 1)
    (4, 1, 0)
    (5, 0, 0)
    """
    if number_of_partitions == 1:
        if natural_number < min_number:
            raise TypeError("Too small 'min_number'.")
        else:
            yield (natural_number,)
    elif number_of_partitions > 1:
        reserved = (number_of_partitions-1) * min_number
        for i in range(min_number, natural_number - reserved + 1):
            for result in number_partition( natural_number-i, number_of_partitions-1, min_number=min_number ):
                yield (i,) + result
    else:
        raise StopIteration
        

def integer_partition(n):
    """
    Source: "http://jeromekelleher.net/tag/integer-partitions.html"

    >>> for partition in integer_partition(5): print(partition)
    [1, 1, 1, 1, 1]
    [1, 1, 1, 2]
    [1, 1, 3]
    [1, 2, 2]
    [1, 4]
    [2, 3]
    [5]
    """
    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2 * x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            yield a[:k + 2]
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        yield a[:k + 1]
        
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()
# Example 1
def calculate_area(radius):
    """
    Calculate the area of a circle given its radius.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The area of the circle.
    """
    pi = 3.14159
    return pi * radius * radius


# Example 2
def find_max(numbers):
    """
    Finds the maximum number in a list of numbers.

    Args:
        numbers (list of int/float): A list of numerical values.

    Returns:
        int/float: The maximum value found in the list.

    Raises:
        ValueError: If the input list is empty.
    """
    max_number = numbers[0]
    for number in numbers:
        if number > max_number:
            max_number = number
    return max_number


# Example 3
def bubble_sort(arr):
    """
    Sorts a list of elements using the bubble sort algorithm.

    :param arr: List of elements to be sorted
    :type arr: list
    :return: Sorted list of elements
    :rtype: list

    :Example:

    >>> bubble_sort([64, 34, 25, 12, 22, 11, 90])
    [11, 12, 22, 25, 34, 64, 90]

    The function works by repeatedly stepping through the list, comparing adjacent elements
    and swapping them if they are in the wrong order. This process is repeated until the list
    is sorted.

    .. note::
        The algorithm has a worst-case and average time complexity of O(n^2), where n is the 
        number of items being sorted.

    .. warning::
        Bubble sort is not suitable for large datasets as its average and worst-case time 
        complexity is quite high.
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
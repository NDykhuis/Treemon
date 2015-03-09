Treemon
=============================

Treemap-based process monitor developed for visualization course in Fall 2010

Illustrates the utility of split treemaps for visualizing resource utilization over time. Averages over the past several seconds for stability of the treemap view. Users can sort by CPU or memory usage, and click boxes in the graphical view to see information about the process.

This is a proof-of-concept, and not meant for practical use. Python+GTK is much too slow for use as a process monitor, and this acquires data inefficiently by parsing the output of "ps aux". 

To run the software:  
 `python treemon.py`
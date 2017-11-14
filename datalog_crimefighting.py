#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 14:38:21 2017

@author: tugg
"""
import pandas as pa
from pyDatalog import pyDatalog


# ---------------------------------------------------------------------------
# Social graph analysis:
# work through this code from top to bottom (in the way you would use a R or Jupyter notebook as well...)
# and write datalog clauses and python code in order to solve the respective tasks. Overall, there are 7 tasks.
# ---------------------------------------------------------------------------
calls = pa.read_csv('calls.csv', sep='\t', encoding='utf-8')
texts = pa.read_csv('texts.csv', sep='\t', encoding='utf-8')

suspect = 'Quandt Katarina'
company_Board = ['Soltau Kristine', 'Eder Eva', 'Michael Jill']

pyDatalog.create_terms('knows', 'has_link', 'X', 'Y', 'Z', 'path', 'P', 'P_old', 'C', 'short_path', 'C_old', 'path2',
                       'D', 'D1', 'has_chron_link', 'has_chron_path', 'chron_knows')
pyDatalog.clear()

# First treat calls simply as social links (denoted knows), which have no date
for i in range(0, 150): # len(calls.index)
    +knows(calls.iloc[i, 1], calls.iloc[i, 2])

# Task 1: Knowing someone is a bi-directional relationship -> define the predicate accordingly
knows(X, Y) <= knows(Y, X)


# Task 2: Define the predicate has_link in a way that it is true if there exists some connection
# (path of people knowing the next link) in the social graph
has_link(X, Y) <= has_link(X, Z) & knows(Z, Y) & (X!=Y)
has_link(X, Y) <= knows(X, Y)


# Hints:
# check if your predictate works: at least 1 of the following asserts should be true
# (2 if you read in all 150 communcation records)
# assert (has_link('Quandt Katarina', company_Board[0]))
# assert (has_link('Quandt Katarina', company_Board[1]))
# assert (has_link('Quandt Katarina', company_Board[2]))


# Task 3: You already know that a connection exists; now give the concrete paths between the board members and the
# suspect
# Hints:
#   if a knows b, there is a path between a and b
#   (X._not_in(P2)) is used to check wether x is not in path P2
#   (P==P2+[Z]) declares P as a new path containing P2 and Z
path(X, Y, P, C) <= knows(X, Y) & (P == []) & (C == 0)
path(X, Y, P, C) <= knows(Z, Y) & (path(X, Z, P_old, C_old)) & (P == P_old+[Z]) & (Z._not_in(P_old)) & (C == C_old+1)

(path2[X, Y, P] == P) <= path(X,Y,P,C) & (C<5)

# print(path2['Quandt Katarina', company_Board[1], P] == P)

# Task 4: There are so many path, therefore we are only interested in short pahts.
# find all the paths between the suspect and the company board, which contain five poeple or less


short_path(X, Y, P) <= path(X, Y, P, C) & (C<=5)
# print(short_path('Quandt Katarina', company_Board[1], P))

# ---------------------------------------------------------------------------
# Call-Data analysis:
# Now we use the text and the calls data together their corresponding dates
# ---------------------------------------------------------------------------
date_board_decision = '12.2.2017'
date_shares_bought = '23.2.2017'
pyDatalog.create_terms('called,texted')
pyDatalog.clear()

for i in range(0,150): # calls
    +called(calls.iloc[i,1], calls.iloc[i,2],calls.iloc[i,3])

for i in range(0,150): # texts
    +texted(texts.iloc[i,1], texts.iloc[i,2],texts.iloc[i,3])

called(X,Y,D) <= called(Y, X, D) # calls are bi-directional


# Task 5: we are are again interested in links, but this time a connection only valid the links are descending in date
# find out who could have actually sent an information, when imposing this new restriction
# Hints:
#   You are allowed to naively compare the dates lexicographically using ">" and "<"; it works in this example of
# concrete dates (but is of course evil in general)
has_chron_link(X, Y, D) <= has_chron_link(X, Z, D1) & chron_knows(Z, Y, D) & (X!=Y) & (D1 <= D)

chron_knows(X, Y, D) <= called(X, Y, D)
chron_knows(X, Y, D) <= texted(X, Y, D)

# print(has_chron_link('Quandt Katarina', Y, D))


# Task 6: at last find all the communication paths which lead to the suspect, again with the restriction that the dates
# have to be ordered correctly
has_chron_path(X, Y, P, D) <= chron_knows(X, Y, D) & (P == []) & (D >= date_board_decision) & (D <= date_shares_bought)

has_chron_path(X, Y, P, D) <= has_chron_path(X, Z, P_old, D1) & chron_knows(Z, Y, D) & (X!=Y) & (D1 <= D)\
                              & (P == P_old + [Z]) & (X._not_in(P_old)) & (Y._not_in(P_old)) & \
                              (D <= date_shares_bought) & (D >= date_board_decision)
print('Connections from ' + company_Board[0] + ':')
print(has_chron_path(company_Board[0], 'Quandt Katarina', P, D))
print('Connections from ' + company_Board[1] + ':')
print(has_chron_path(company_Board[1], 'Quandt Katarina', P, D))
print('Connections from ' + company_Board[2] + ':')
print(has_chron_path(company_Board[2], 'Quandt Katarina', P, D))


# Final task: after seeing this information, who, if anybody, do you think has given a tipp to the suspect?




# General hint (only use on last resort!):
#   if nothing else helped, have a look at https://github.com/pcarbonn/pyDatalog/blob/master/pyDatalog/examples/graph.py
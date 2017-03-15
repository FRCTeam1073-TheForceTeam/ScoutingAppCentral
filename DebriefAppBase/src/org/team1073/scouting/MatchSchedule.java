package org.team1073.scouting;

import java.util.List;

// Class definition for the match schedule that is retrieved from the Central App server. The
// match schedule is contained in a JSON formatted file consisting of a set of string arrays
// for each match within the different rounds:
//		- qualification round (qm)
//		- quarter finals (qf)
//		- semi finals (sf)
//		- finals (f)
//
// The 'columns' element is a list of strings that correspond to the format of each match entry.
// The application can use the columns to determine which array element to access within the
// match entry.
//
// The columns element will be something like the following:
//
//		[ 'Round', 'Match', 'Red_1', 'Red_2', 'Red_3', 'Blue_1', 'Blue_2', 'Blue_3' ]
//
// And a corresponding match entry would be:
//
//		[ 'qm', '1', '3466', '5491', '2423', '5422', '238', '3780' ]
//
// For the quarter-finals, and semi-finals rounds, the match number itself will be formatted as
// a combination of the round number and the match number, separated by a dash '-'. For example, 
// match 1 in quarterfinal round 2 will be formatted as '2-1', as shown below
//
//		[ 'qf', '2-1', '3467', '246', '1073', '811', '1100', '4908' ]
//
public class MatchSchedule {
	String			event;
	List<String>	columns;
	List<String[]>	qualification;
	List<String[]>	quarter_finals;
	List<String[]>	semi_finals;
	List<String[]>	finals;
}

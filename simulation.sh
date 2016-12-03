#! /bin/bash

. /vol/customopt/lamachine/bin/activate

PP=1
maxPP=3
maxGen=1460
while [ $PP -le $maxPP ]
do
	echo Simulating participant $PP...
	gen=0
	while [ $gen -le $maxGen ]
	do
		if [ $gen -eq 0 ]
		then
			echo Simulating participant $PP Initializing Noun lexicon.
			python makeLexicon.py $PP $gen $maxPP $maxGen
			timbl -f lexicon.train -t leave_one_out -k3 -w0 -mO:I1-3 -o production.test.out > Timbl_simulation_output.txt
			echo Simulating participant $PP Initializing Adjective lexicon.
			python makeLexicon_adj.py $PP $gen $maxPP $maxGen
			timbl -f adj_lexicon.train -t leave_one_out -k3 -w0 -mO:I1,2 -o adj_production.test.out >> Timbl_simulation_output.txt
		else
			echo Simulating participant $PP generation $gen for nouns.
			python makeLexicon.py $PP $gen $maxPP $maxGen
			timbl -f lexicon.train -t production.test -k1 -w0 -mO:I1-3 -o production.test.out >> Timbl_simulation_output.txt
			timbl -f lexicon.train -t experiment.test -k1 -w0 -mO:I1-3 -o experiment.test.out >> Timbl_simulation_output.txt
			echo Simulating participant $PP generation $gen for adjectives.
			python makeLexicon_adj.py $PP $gen $maxPP $maxGen
			timbl -f adj_lexicon.train -t adj_production.test -k1 -w1 -mO:I1,2 -o adj_production.test.out >> Timbl_simulation_output.txt
			timbl -f adj_lexicon.train -t adj_experiment.test -k1 -w1 -mO:I1,2 -o adj_experiment.test.out >> Timbl_simulation_output.txt
		fi
		((gen++))
	done
	timbl -f adj_lexicon.train -t adj_exceptions.test -k1 -w1 -mO:I1,2 -o adj_exceptions.test.out >> Timbl_simulation_output.txt
	python makeLexicon.py $PP $gen $maxPP $maxGen
	python makeLexicon_adj.py $PP $gen $maxPP $maxGen
	rm dic_list.pck lexicon.train adjective_dict_list.pck adj_lexicon.train
	((PP++))
done

rm adj_experiment.test adj_experiment.test.out adj_production.test adj_production.test.out adj_results.pck experiment.test experiment.test.out production.test production.test.out results.pck noun_input.txt adj_exceptions.test adj_exceptions.test.out


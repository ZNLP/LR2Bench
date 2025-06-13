# for task in 0-crossword 1-acrostic 2-logic 3-cryptogram 4-sudoku 5-drop; do
for task in 0-crossword; do
    bash gen.sh "4,5,6,7" $task "qwen-2.5-7b" 0.0 1.0
done
# Nearest-Neighbor-GPX
Takes a list of coordinates and creates a GPX file of the optimal (shortest) path.

Calculates the distance between two coordinates using the Haversine Formula and greedily goes from there.

It returns the shortest value, but it is not necessarily the most optimal path.

Problems to fix:
- RUNTIME
- The ability to choose a starting point
- Maybe implement a more sophisticated algorithm that can do better than greedy
- More and more tests!
- Develop a NP complete solution to the Traveling Salesman Problem (lol.)

User Guide:
1. Have Python 3 installed.
2. Make sure your text file is in the same directory as the script.
3. Make sure your text file only contains coordinates, it does not work with N,S,E,W formatted coordinates. NO SPACES!
4. Run script.
5. Place GPX file where ever you want.

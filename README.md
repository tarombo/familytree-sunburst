# familytree-sunburst
Forked by arnold+test@kopoka.com

Produce a family treee display, from a GEDCOM file, which can be viewed/zoomed/hovered in a web browser.

![example as image](https://github.com/johnandrea/familytree-sunburst/blob/master/examples/family.png)

The display is based on the D3.js Zoomable Sunburst:
https://bl.ocks.org/vasturiano/12da9071095fbd4df434e60d52d2d58d
  Circle sections are clickable to zoom into that section and descendants.
Clicking on the center of circle will zoom out.

In the produced family tree diagram, person details are shown when the mouse
hovers over a circle section.

The included program "read-ged.py" requires Python3 to convert a GED file
to the JSON format which is read by the Javascript display tool.
   The examples use the name family.json for the converted filename, but any
name may be used so long as the name matches the name used in the HTML file.

To produce the output file you must supply the ID from the GED file for the
person you wish to use as the "start" of the display.

The included read-ged.py program can produce info about a GED file:

To get a listing of all the names in the file, with the
GED id as the first item on each line:

     read-ged.py  family.ged   list
	 
To list only the persons which don't have any parents in the file:

     read-ged.py  family.ged   noparents

To get a count of the maxium number of generations for each person,
with the count as the first item on each line:

     read-ged.py  family.ged  generations

Using those outputs to determine the ID of the "start" person.
Output a JSON format file, ready for the visualization:

     read-ged.py  family.ged  json  person-ged-id > family.json

# edtf-arches-hip
Extended Date/Time Format for Arches Heritage Inventory Package

## Synopsis

This project demonstrates a method of supporting a wider range of dates in [Arches](https://github.com/archesproject/arches)/[Arches-HIP](https://github.com/archesproject/hip) fields based on the [Library of Congress' Extended Date/Time Format 1.0](http://www.loc.gov/standards/datetime/pre-submission.html) or EDTF. In addition to accepting valid EDTF entries, this feature also recognizes a wide-range of human inputs (e.g. December 12, 2004) and suggests the correct format for the user to enter (e.g. 2004-12-12).

## Motivation

By default, date fields in Arches-HIP (i.e. *.E49 in CIDOC-CRM) are formatted as dates in PostgreSQL with further validation provided by Bootstrap Datepicker, requiring the user to enter a fully-formatted date of type YYYY-MM-DD. Additionally, [PostgreSQL does not support dates earlier than 4713 BC](http://www.postgresql.org/docs/current/static/datatype-datetime.html). Because heritage inventories often deal with "fuzzy" dates (e.g. approximate, unknown, unspecified) as well as very early dates (primarily for archaeological sites), we wanted to explore how such dates could be supported in Arches while maintaining data consistency. 

The [LOC EDTF](http://www.loc.gov/standards/datetime/) provides an extension to [ISO 8601](http://www.iso.org/iso/home/standards/iso8601.htm), which allows for the specification of varying levels of "fuzzy" dates such as "approximately 1884", "sometime in the 1910s", or "10000 BC/BCE".  


## Supported Formats
This project currently supports the following levels of features as specified in [EDTF](http://www.loc.gov/standards/datetime/pre-submission.html#features):

### Level 0. ISO 8601 Features

| Feature       | Format | Examples | Notes |
| ------------- | -------| -------- | ----- |
| Date	        | YYYY-MM-DD |2001-02-03||
|				| YYYY-MM |	2008-12||
|				| YYYY	|	2008	||
|				| negative years | -0999	||
|				| year zero | 0000  ||
| Interval      | YYYY / YYYY | 1964 / 2008 | The project only implements intervals in paired FROM_DATE.49 and TO_DATE.49 entities|
| (from / to)	| YYYY-MM/YYYY-MM | 2004-06/2006-08 ||
| 				| YYYY-MM-DD/YYYY-MM-DD | 2004-02-01/2005-02-08||
|				| YYYY-MM-DD/YYYY-MM | 2004-02-01/2005-02||
|				| YYYY-MM-DD/YYYY 	| 2004-02-01/2005 ||
|				| YYYY/YYYY-MM		| 2005/2006-02 ||

### Level 1 Extensions

| Feature       | Format | Examples | Notes |
| ------------- | -------| -------- | ----- |
|Uncertain | YYYY?  | 1984? | EDTF definition of Uncertain: A date or date/time is considered "uncertain" when...[one]... determines...that its source is dubious.|
| | YYYY-MM? | 1900-02? ||
| | YYYY-MM-DD? | 1872-03-23? ||
|Approximate | YYYY~ | 1800~ | EDTF definition of Approximate: An estimate whose value is asserted to be possibly correct, and if not, close to correct.|
||YYYY-MM~|1900-02~||
|Uncertain Approximation| YYYY?~ | 1789?~ ||
|Unspecified| YYYu | 178u | EDTF definition of Unspecified: The value is unstated. It could be because the date (or part of the date) has not (yet) been assigned...or because it is classified, or unknown, or for any other reason. (e.g. illegibility)|
||YYuu|17uu||
||YYYY-uu|1780-uu||
| Extended Intervals | unknown/YYYY |unknown/2000|The project only implements intervals in paired FROM_DATE.49 and TO_DATE.49 entities |
||YYYY-MM-DD/unknown|1899-03-03/unknown||
||YYYY-MM-DD/open|1934-02-03/open |Open is used when a condition or chronological span has not yet ended -- this can be very useful, for instance, in the classification or designation sections to indicate current usage or designations remain in effect.|
||YYYY~/YYYY-DD ... |1879~/1965-02|Any combination of approximate (~) and uncertain (?) can be entered as extended intervals in FROM_DATE.49 and TO_DATE.49 entities.|
|Year exceeding four digits| YYYYYY or -YYYYYY | -240000 | In order to retain numeric integrity when sorting, this project departs from the EDTF format (which precedes such dates with 'y') and supports years of 5 or 6 digits.| 

### Level 2 Extensions

| Feature       | Format | Examples | Notes |
| ------------- | -------| -------- | ----- |
|Masked precision | YYYx | 196x | EDTF states: Note the difference in semantics between 'x' and 'u'. '196x' has decade precision while '196u' has year precision. Both represent an unspecified year during the 1960s, but for 196x the year is not supplied because it is known only with decade precision. In contrast, for 196u the year is not supplied for reasons that are not specified but there is some expectation (though no guarantee) that the year may be supplied later; for 196x there is no such expectation.|
|| YYxx| 19xx||


## Installation
*Ideally, this feature should be implemented during the Arches installation process because it requires changes to the resource graphs, specifically redefining entity types. Midstream deployment has not been tested.*

Because each Arches project has different data needs, these instructions will guide you through the process of adding EDTF support to any date field you choose. This Github repository demonstrates the application of EDTF support to a limited set of Arches date fields. We recommend using this repository as a working reference or demonstration of the EDTF support feature. 

### Step 1: Analyze Your Project's Needs
Analyze your data needs while consulting the [Arches-HIP resource graphs](https://arches-hip.readthedocs.io/en/latest/hip-resources/#hip-graphs) in order to decide which dates should remain in standard date format, and which should be in EDTF. 

This repository demonstrates the EDTF support feature on the following entities:
- FROM_DATE.E49
- TO_DATE.E49
- START_DATE_OF_EXISTENCE.E49
- END_DATE_OF_EXISTENCE.E49 


### Step 2: Edit the Resource Graphs
Find the corresponding entities in your `projects/my_hip_app/my_hip_app/source_data/*.E*_nodes.csv` files (this project's directory structure uses "archesdev" in place of my_hip_app). 

Edit "dates" to "strings" at the end of each corresponding line. 


For instance, if you wanted to change START_DATE_OF_EXISTENCE.E49 to EDTF, you would have to make these edits across all the concept files that define the use of that entity. In this demonstration, START_DATE_OF_EXISTENCE.E49 has been changed in the following files and lines:
-  ACTIVITY.E7_nodes.csv:675
-  ACTOR.E39_nodes.csv:38
-  HERITAGE_RESOURCE.E18_nodes.csv:159
-  HERITAGE_RESOURCE_GROUP.E27_nodes.csv:506
-  HISTORICAL_EVENT.E5_nodes.csv:673

### Step 3: Create the Database 
Create the database the same way you would for a default Arches-HIP installation (remember this project's directory structure uses "archesdev" in place of "my_hip_app" in case you are working from this project's files):

```
$ cd projects
$ source ENV/bin/activate
(ENV)$ cd my_hip_app
(ENV)$ python manage.py packages -o install
```
(Loading data and running Arches and its services proceeds just as normal.)

### Step 4: Install the Javascript Dependencies
This project relies upon three javascript packages:
- [Bootbox.js](http://bootboxjs.com/)
- [Edtfy.js](https://github.com/nicompte/edtfy)
- [Moment.js](http://momentjs.com/)

These should be installed in the following directory: `projects/my_hip_app/my_hip_app/media/js/plugins/`. You can either copy them directly from this project's repository or use a package manager such as [npm](https://www.npmjs.com/) or [bower](http://bower.io/). 

### Step 5: Load the Dependencies
Copy this project's base.htm file (found in `archesdev/archesdev/templates`) into your project's template folder. 

*In case you want to know why you have to do this:* It's not enough to place javascript modules into your project's media folder -- you also have to tell Arches to look for them. Arches uses [require.js](http://requirejs.org/) to manage such dependencies, and it does so in the base.htm template file (which is, as the name implies, the base for all of Arches' html content).

Arches' base template file can be found in `projects/ENV/lib/python2.7/site-packages/arches/app/templates`. However, you should NOT edit the file here. Instead, you will want to place your project's specific overrides into your project's local template folder at `projects/my_hip_app/my_hip_app/templates`. Any template file that you place here will overwrite the default Arches template. 

### Step 6: Install the EDTF validation function
Copy this project's branch-list.js file (found in `archesdev/archesdev/media/js/views/forms/sections`) into your project's corresponding directory (e.g. `projects/my_hip_app/my_hip_app/media/js/views/forms/sections`.)

This file introduces a new validation function, validateEdtfy, which you can call on any field to provide EDTF validation. 

### Step 7a: Override the Form Fields' Display (html)
For each form field you wish to change to EDTF, you will need to edit its html in the corresponding template file. The default template files for forms are stored in `projects/ENV/lib/python2.7/site-packages/arches_hip/templates/views/forms`. Like the base.htm file, you can override these files with a modified copy in your project's local templates folder (e.g. projects/my_hip_app/my_hip_app/templates/views/forms). 

This project demonstrates the necessary changes on three forms: 
- classification.htm
- historical-event-summary.htm
- summary.htm

If these correspond to your needs, you can copy these files into your local templates/views/forms directory, or compare the differences to apply them to a different form.

Changes have been made to the form's input field to remove the Bootstrap Datepicker and to edit the alert message that displays when data in an unsupported format is entered.

### Step 7b: Override the Form Fields' Validation (javascript)
For each form field you wish to change to EDTF, you will also have to edit the validation function it uses in a corresponding javascript file. The default javascript files are stored in `projects/ENV/lib/python2.7/site-packages/arches_hip/media/js/views/forms`. You can override these files with a modified copy in your project's local media folder (e.g. projects/my_hip_app/my_hip_app/media/js/views/forms). 

This project demonstrates the necessary changes on three forms: 
- classification.js
- historical-event-summary.js
- summary.js

If these correspond to your needs, you can copy these files into your local media/js/views/forms directory, or compare the differences to apply them to a different form.

The only change made is in calling the new validateEdtfy function from `return this.validateHasValues(nodes);` to `return this.validateEdtfy(nodes);`   


## Testing
If you are running Arches in production using a web server like Apache, you will need to restart Apache to view changes to the template files. Access your modified Resource Manager form and try entering the dates given in the Supported Formats table above. 

If a user enters a date that is not in correct EDTF format, but is in a recognizable format (e.g. "about 1900") the program will display a Bootbox Modal window with a corrected entry (e.g. 1900~).

## Extending Further
EDTF stands for "Extended Date/Time Format"; although this project by default only supports Date formats, it would likely be possible to add datetime support.  

In that case, you would want to start by examining the validateEdtfy function in branch-list.js and edit Line 83, where the moment.js formats are defined as an array.
``` var formats = ["YYYY-MM-DD", "YYYY-MM", "Y"]; ```

We welcome issue reports and contributions!

## Note
The deployment of this feature impacts the Timespan search filter bar and may, in fact, disable it. However because EDTF retains alphanumeric sorting integrity, the Start/End Dates section of the time filter can still be used.

## Credits
This project uses the [edtfy parser built and maintained by Nicolas Barbotte](https://github.com/nicompte/edtfy), who was very responsive with our questions. We would also like to recognize the [work that the University of North Texas Library](http://digital.library.unt.edu/ark:/67531/metadc174739/) has done in implementing EDTF validation with a very cool [Django app](https://github.com/unt-libraries/django-edtf). If EDTF were to be taken up in version 4 of Arches, their AJAX-based validator might be the ticket!

## License

This feature is released under the [GNU Affero General Public License, 3.0 (AGPL) license](http://www.gnu.org/licenses/agpl.html).

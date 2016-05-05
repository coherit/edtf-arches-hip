# edtf-arches-hip
Extended Date/Time Format for Arches Heritage Inventory Package

## Synopsis

This project demonstrates how to support a wider range of dates in [Arches](https://github.com/archesproject/arches)/[Arches-HIP](https://github.com/archesproject/hip) fields based on the [Library of Congress' Extended Date/Time Format 1.0](http://www.loc.gov/standards/datetime/pre-submission.html) or EDTF. 

## Motivation

By default, date fields in Arches-HIP (i.e. E*.49 in CIDOC-CRM) are formatted as dates in PostgreSQL with further validation provided by Bootstrap Datepicker, requiring the user to enter a fully-formatted date of type YYYY-MM-DD. Additionally, [PostgreSQL does not support dates earlier than 4713 BC](http://www.postgresql.org/docs/current/static/datatype-datetime.html). Because heritage inventories often deal with "fuzzy" dates (e.g. approximate, unknown, unspecified) as well as very early dates, we wanted to explore how such dates could be supported in Arches while maintaining data consistency. 

The [LOC EDTF](http://www.loc.gov/standards/datetime/) provides an extension to [ISO 8601](http://www.iso.org/iso/home/standards/iso8601.htm), which allows for the specification of varying levels of "fuzzy" dates such as "approximately 1884", "sometime in the 1910s", or (10000 BCE).  


## Supported Formats
This project is currently supporting the following levels of features as specified in [EDTF](http://www.loc.gov/standards/datetime/pre-submission.html#features):
###Level 0. ISO 8601 Features
| Feature       | Format | Examples | Notes |
| ------------- | -------| -------- | ----- |
| Date	        | YYYY-MM-DD |2001-02-03||
|				| YYYY-MM |	2008-12||
|				| YYYY	|	2008	||
|				| YYYY BCE | -0999	||
|				| year zero | 0000  ||
| Interval      | YYYY/YYYY | 1964/2008 | The project only implements intervals in paired FROM_DATE.49 and TO_DATE.49 entities|
| (from / to)	| YYYY-MM/YYYY-MM | 2004-06/2006-08 ||
| 				| YYYY-MM-DD/YYYY-MM-DD | 2004-02-01/2005-02-08||
|				| YYYY-MM-DD/YYYY-MM | 2004-02-01/2005-02||
|				| YYYY-MM-DD/YYYY 	| 2004-02-01/2005 ||
|				| YYYY/YYYY-MM		| 2005/2006-02 ||

###Level 1 Extensions
| Feature       | Format | Examples | Notes |
| ------------- | -------| -------- | ----- |


## Installation

Provide code examples and explanations of how to get the project.

## API Reference

Depending on the size of the project, if it is small and simple enough the reference docs can be added to the README. For medium size to larger projects it is important to at least provide a link to where the API reference docs live.

## Tests

Describe and show how to run the tests with code examples.

## Credits
This project uses the [edtfy parser built by Nicolas Barbotte](https://github.com/nicompte/edtfy). 

## License

A short snippet describing the license (MIT, Apache, etc.)
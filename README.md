**excelfee** - web-application that uses REST API to calculate data via MS Excel files without MS Excel installed.

Input: 
* Excel file (Base64 encoded) 
* Cell pointers (coordinates of cells) with values to update
* Cell pointers that are expected to get as a result

Output: 
* Cells objects (each cell - JSON) that contains:
    * Cell coordinate
    * Cell value type (Numeric, Text)
    * Cell value (separate tags for numeric and text)
    
The application purpose is to provide Excel capabilities to programming languages without Excel-handling libraries via generic REST API endpoint
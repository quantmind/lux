## Forms

* Select field changes [[#249](https://github.com/quantmind/lux/pull/249)]
    * Stop pre-selecting the first option in select fields
        * For ui-select selects, this uses the placeholder functionality. For standard selects, this uses a 'Please select...' option.
    * Allows the value of non-required select field to be cleared
    * Correctly sets the required attribute for ui-select selects
    * Makes the display value for ui-select fields use the repr value if available

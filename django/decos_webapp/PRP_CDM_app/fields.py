# Copyright (c) 2025 Marco Prenassi
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description:
# This module defines custom Django form widgets for improved form interaction in web applications.
# - MultiChoicheAndOtherWidget: Provides a dropdown selection with an optional text field for additional input.
# - BooleanIfWhat: Implements a checkbox allowing users to specify a reason when selecting 'No' or 'Yes'.
# Security enhancements include input sanitization and template whitelisting to mitigate potential risks.

from django import forms
import html

# Define allowed template names to mitigate injection risks
ALLOWED_TEMPLATES = {"jsmultipleandother.html", "jsbooleanifwhat.html"}

# Multi-widget combining a dropdown with an additional text input
class MultiChoicheAndOtherWidget(forms.MultiWidget):
    template_name = "jsmultipleandother.html"

    def __init__(self, choices):
        if self.template_name not in ALLOWED_TEMPLATES:
            raise ValueError("Invalid template name")
        
        choices = choices + [('other', 'other')]
        widgets = [
            forms.Select(choices=choices),  # Dropdown for predefined choices
            forms.TextInput(attrs={'placeholder': 'Other'}),  # Text input for custom entries
        ]
        super().__init__(widgets)

    def decompress(self, value):
        # Convert stored value into separate components for the widget
        if not value:
            return [None, None]
        return value

    def value_from_datadict(self, data, files, name):
        # Extracts and processes data from the form submission
        value1, value2 = super().value_from_datadict(data, files, name)
        if value1 == 'Other':
            return 'Other: {}'.format(html.escape(value2))  # Escaping user input to prevent injection
        else:
            return value1

    def subwidgets(self, name, value, attrs=None):
        # Returns subwidgets to be rendered individually
        context = self.get_context(name, value, attrs)
        return context['widget']['subwidgets']

# Checkbox widget allowing users to provide a reason when selecting 'No' or 'Yes'
class BooleanIfWhat(forms.MultiWidget):
    template_name = "jsbooleanifwhat.html"
    yes_or_no = False

    def __init__(self, yes_or_no):
        if self.template_name not in ALLOWED_TEMPLATES:
            raise ValueError("Invalid template name")
        
        widgets = [
            forms.CheckboxInput(),  # Checkbox input for Yes/No selection
            forms.TextInput(attrs={'placeholder': '...'}),  # Optional text input for explanations
        ]
        self.yes_or_no = bool(yes_or_no)  # Ensures consistent boolean representation
        super().__init__(widgets)

    def decompress(self, value):
        # Splits the stored value into checkbox state and text input content
        if not value:
            return [None, None]
        if value == 'Yes':
            return [True, '']  # Checkbox checked, text field hidden
        if value.startswith('Yes:'):
            return [True, value[5:].strip()]
        elif value.startswith('No:'):
            return [False, value[4:].strip()]
        return [None, value]

    def value_from_datadict(self, data, files, name):
        # Processes input data and formats it appropriately for storage
        value1, value2 = super().value_from_datadict(data, files, name)
        if bool(value1) == self.yes_or_no:
            return '{}: {}'.format('Yes' if self.yes_or_no else 'No', html.escape(value2.strip()))
        else:
            return 'No: {}'.format(html.escape(value2.strip())) if self.yes_or_no else 'Yes: {}'.format(html.escape(value2.strip()))

    def subwidgets(self, name, value, attrs=None):
        # Retrieves subwidgets for rendering
        context = self.get_context(name, value, attrs)
        return context['widget']['subwidgets']

    def get_context(self, name, value, attrs):
        # Generates widget context with additional attributes
        attrs = attrs or {}
        attrs['yes_or_no'] = self.yes_or_no
        context = super().get_context(name, value, attrs)
        return context

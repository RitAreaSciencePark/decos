# PRP_CDM_app - Forms Module Documentation

## Overview

The **Forms Module** in `PRP_CDM_app` provides a structured way to **decouple the ontology structure from form structures**, allowing a **single form to collect data from multiple tables**. It is designed to facilitate **efficient and standardized metadata collection** while ensuring user-friendly input interfaces for laboratory sample data.

This module **enables form customization** for different laboratories within the **DECOS system**, ensuring that each lab has a **tailored metadata input structure** while maintaining compliance with the **Common Data Model (CDM)**.

## Key Features

- **Ontology-Decoupled Form Structure**  
  - Forms do not directly mirror the database schema, allowing more **flexible user input interfaces**.
  - Supports multiple laboratory-specific sample models.

- **Laboratory-Specific Forms**  
  - Forms are customized for individual laboratories.
  - Excludes non-relevant or system-managed fields.

- **Standardized Metadata Collection**  
  - Ensures **consistent data formatting** across different labs.
  - Facilitates integration with **DECOS Common Data Model (CDM)**.

## Form Definitions

The module defines forms within the `FormsDefinition` class, grouping laboratory-specific form structures.

### **1. `LageForm` (LAGE Laboratory Samples Form)**

Handles sample metadata input for the **LAGE laboratory**.

- **Associated Model**: `LageSamples`
- **Excluded Fields**:
  - `sr_id`: Service Request ID (managed internally)
  - `sample_id`: Sample identifier (automatically assigned)
  - `lab_id`: Laboratory identifier (predefined)
  - `sample_feasibility`: Internal evaluation field
  - `sample_status`: System-managed status tracking
  - `sample_location`: Internal laboratory storage location

### **2. `LameForm` (LAME Laboratory Samples Form)**

Handles sample metadata input for the **LAME laboratory**.

- **Associated Model**: `LameSamples`
- **Excluded Fields**:
  - `sr_id`: Service Request ID (managed internally)
  - `sample_id`: Sample identifier (automatically assigned)
  - `sample_feasibility`: Internal evaluation field
  - `sample_status`: System-managed status tracking
  - `sample_location`: Internal laboratory storage location

## Integration with DECOS

This forms module integrates with:
- **Common Data Model (CDM)**: Ensuring **semantic consistency** across different laboratories.
- **Laboratory-Specific Extensions**: Forms dynamically adapt to **LAGE** and **LAME** laboratory models (`lage.py`, `lame.py`).
- **Metadata Collection Pipelines**: Standardizing how sample-related data is inputted, stored, and processed.

## License

This module is part of the **DECOS system** and is licensed under the **MIT License**. See the `LICENSE` file in the project root for details.

## Authors

Developed by **Marco Prenassi** and **Cecilia Zagni**,  
Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.

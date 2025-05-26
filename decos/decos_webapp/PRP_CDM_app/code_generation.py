# Copyright (c) 2025 Marco Prenassi, Cecilia Zagni,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi, Cecilia Zagni
# Date: 2025-02-17
# Description:
# This file defines functions to generate unique identifiers for proposals, service requests, samples, 
# instruments, and results in the PRP_CDM_app. It ensures structured and standardized metadata across 
# different entities while handling progressive numbering efficiently.

import re
import logging
import random as rd
from datetime import datetime
from uuid import uuid4
from PRP_CDM_app.models.common_data_model import Proposals, ServiceRequests, Samples

# Logger setup for error tracking
logger = logging.getLogger(__name__)

# Constants
RANDOM_SUFFIX_RANGE = (1000, 9999)  # Range for random suffix generation
TRUNCATE_LENGTH = 22  # Maximum length for xid_code relations

# Shortens an affiliation by keeping the first 4 non-space characters
def affiliation_shortener(affiliation):
    if not affiliation:  
        logger.warning("affiliation_shortener received None or empty string")  
        return "UNK"  # Default to 'UNK' (Unknown) if None or empty
    
    return "".join(affiliation.strip().split())[:4]

# Generates a unique instrument ID by combining model, vendor, and a random suffix
def instrument_id_generation(model, vendor):
    model = model.lower()
    instrument_id = re.sub(r'[^A-Za-z0-9_]', '', f"{model}_{vendor}")
    instrument_id += f"_{rd.randint(*RANDOM_SUFFIX_RANGE)}"
    return instrument_id

# Generates a proposal ID with a progressive number based on the latest proposal
def proposal_id_generation(affiliation):
    try:
        last_proposal = Proposals.objects.latest('proposal_id')
        match = re.search(r'_(\d+)$', last_proposal.proposal_id)
        last_progressive = int(match.group(1)) if match else 0
    except Proposals.DoesNotExist:
        last_progressive = 0
    except Exception as e:
        logger.error(f"Unexpected error in proposal_id_generation: {e}")
        raise

    return f"p_{datetime.now().year}_{affiliation_shortener(affiliation)}_{last_progressive + 1:05d}"

# Generates a service request (SR) ID based on proposal and lab, ensuring a progressive sequence
def sr_id_generation(proposal, lab):
    try:
        last_sr = ServiceRequests.objects.latest('sr_id')
        match = re.search(r'_(\d+)$', last_sr.sr_id)
        last_progressive = int(match.group(1)) if match else 0
    except ServiceRequests.DoesNotExist:
        last_progressive = 0
    except Exception as e:
        logger.error(f"Unexpected error in sr_id_generation: {e}")
        raise

    return f"sr_{proposal.proposal_id[2:]}_{lab.lab_id}_{last_progressive + 1:05d}"

# Generates a unique sample ID based on the service request (SR) ID or assigns an internal ID
def sample_id_generation(sr_id):
    try:
        last_sample = Samples.objects.latest('sample_id')
        match = re.search(r'_(\d+)$', last_sample.sample_id)
        last_progressive = int(match.group(1)) if match else 0
    except Samples.DoesNotExist:
        last_progressive = 0
    except Exception as e:
        logger.error(f"Unexpected error in sample_id_generation: {e}")
        raise

    if sr_id and len(sr_id) > 3:
        return f"s_{sr_id[3:]}_{last_progressive + 1:05d}"
    return f"s_internal_{last_progressive + 1:05d}"

# Generates a UUID-based result ID (ignores 'data' but allows it as an optional parameter)
def result_id_generation(data=None):
    return str(uuid4())  # Keeping it as a UUID, ignoring 'data' if passed

def experimentdmp_id_generation(data=None):
    return str(uuid4())  # Keeping it as a UUID, ignoring 'data' if passed

# Generates a cross-identifier (XID) by concatenating two related IDs with truncation
def xid_code_generation(relation_id_1, relation_id_2):
    return f"{relation_id_1[-TRUNCATE_LENGTH:]}_x_{relation_id_2[-TRUNCATE_LENGTH:]}"

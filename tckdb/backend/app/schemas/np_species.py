"""
TCKDB backend app schemas non-physical species (np_species) module
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field, validator, constr, conint

try:
    from rmgpy.molecule.adjlist import from_adjacency_list
except ImportError:
    # These modules are not in the requirements.txt file (cannot be installed via pip) and are skipped if not present
    pass

import tckdb.backend.app.schemas.common as common
import tckdb.backend.app.conversions.converter as converter


class NonPhysicalSpeciesBase(BaseModel):
    """
    A NonPhysicalSpeciesBase class (shared properties)
    """
    label: Optional[str] = Field(None, max_length=255, title='Species label')
    timestamp: Optional[float] = Field(None, gt=1.58E9, title='Time stamp')  # 1.58E9 corresponds to 2020-01-25 19:53:20
    retracted: Optional[str] = Field(None, max_length=255, title='Retracted')
    reviewed: Optional[bool] = Field(None, title='Retracted (bool)')
    approved: Optional[bool] = Field(None, title='Approved (bool)')
    charge: int = Field(..., ge=-10, le=10, title='Net charge')
    multiplicity: int = Field(..., ge=1, le=10, title='Spin multiplicity')
    smiles: Optional[str] = Field(None, max_length=5000, title='SMILES')
    inchi: Optional[str] = Field(None, max_length=5000, title='InChI')
    inchi_key: Optional[str] = Field(None, max_length=27, min_length=27, title='InChI key')
    graph: Optional[str] = Field(None, max_length=100000, title='Adjacency list graph')
    electronic_state: Optional[str] = Field('X', max_length=150, title='Electronic state')
    coordinates: Dict[str, Union[Tuple[Tuple[float, float, float], ...],
                                 Tuple[conint(ge=1), ...],
                                 Tuple[constr(max_length=10), ...]]] = Field(..., title='Cartesian coordinates')
    fragments: Optional[List[List[conint(ge=1)]]] = Field(None, title='Fragments')
    fragment_orientation: Optional[List[Dict[str, Union[float, List[float]]]]] = Field(None, title='Fragment orientation')
    chirality: Optional[Dict[Tuple[conint(ge=1), ...], constr(max_length=10)]] = Field(None, title='Chirality')
    conformation_method: Optional[constr(max_length=500)] = Field(None, title='Conformarion method')
    is_well: bool = Field(..., title='Is this species a well on the PES?')
    is_global_min: Optional[bool] = Field(None, title='If this conformer is a well, whether it is meant to represents '
                                                      'the **global** minimum energy well')
    global_min_geometry: Optional[Dict[str, Union[Tuple[Tuple[float, float, float], ...],
                                                  Tuple[conint(ge=1), ...],
                                                  Tuple[constr(max_length=10), ...]]]] = \
        Field(None, title='If this species does not represent the global minimum well, this argument must contain '
                          'the coordinates of the global minimum energy conformer at the same opt level.')
    is_ts: bool = Field(False, title='Does this species represent a transition state?')
    irc_trajectories: Optional[List[List[Dict[str, Union[Tuple[Tuple[float, float, float], ...],
                                              Tuple[conint(ge=1), ...], Tuple[constr(max_length=10), ...]]]]]] = \
        Field(None, title='IRC trajectories (for TS species)')
    opt_path: Optional[str] = Field(None, max_length=5000, title='Path to optimization log file')
    freq_path: Optional[str] = Field(None, max_length=5000, title='Path to frequencies log file')
    scan_paths: Optional[Dict[Tuple[Tuple[conint(ge=1), conint(ge=1), conint(ge=1), conint(ge=1)], ...],
                              constr(max_length=5000)]] = Field(None, title='Paths to scan log files')
    irc_paths: Optional[List[constr(max_length=5000)]] = Field(None, title='Paths to IRC log files')
    sp_path: Optional[str] = Field(None, max_length=5000, title='Path to single-point energy log file')
    unconverged_jobs: Optional[List[Dict[str, str]]] = Field(None, title='Paths to unconverged job log files')
    extras: Optional[Dict[str, Any]] = Field(None, title='Extras')
    reviewer_flags: Optional[Dict[str, str]] = Field(None, title='Reviewer flags')

    class Config:
        extra = "forbid"

    @validator('reviewer_flags', always=True)
    def check_reviewer_flags(cls, value):
        """NonPhysicalSpecies.reviewer_flags validator"""
        return value or dict()

    @validator('timestamp', always=True)
    def assign_timestamp(cls, value):
        """NonPhysicalSpecies.timestamp validator"""
        return datetime.timestamp(datetime.utcnow())

    @validator('retracted')
    def retracted_validator(cls, value, values):
        """NonPhysicalSpecies.retracted validator"""
        label = f' (non-physical-species label: "{values["label"]}")' \
            if 'label' in values and values['label'] is not None else ''
        if value is not None:
            raise ValueError(f'The "retracted" argument is not a user input{label}.')
        return None

    @validator('reviewed', always=True)
    def reviewed_validator(cls, value, values):
        """NonPhysicalSpecies.reviewed validator"""
        label = f' (non-physical-species label: "{values["label"]}")' \
            if 'label' in values and values['label'] is not None else ''
        if value is not None:
            raise ValueError(f'The "reviewed" argument is not a user input{label}.')
        return False

    @validator('approved', always=True)
    def approved_validator(cls, value, values):
        """NonPhysicalSpecies.approved validator"""
        label = f' (non-physical-species label: "{values["label"]}")' \
            if 'label' in values and values['label'] is not None else ''
        if value is not None:
            raise ValueError(f'The "approved" argument is not a user input{label}.')
        return False

    @validator('smiles')
    def smiles_validator(cls, value, values):
        """NonPhysicalSpecies.smiles validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        is_valid, err = common.is_valid_smiles(value)
        if not is_valid:
            raise ValueError(f'The SMILES "{value}"{label} is invalid. Reason:\n{err}')
        return value

    @validator('inchi')
    def inchi_validator(cls, value, values):
        """NonPhysicalSpecies.inchi validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        is_valid, err = common.is_valid_inchi(value)
        if not is_valid:
            raise ValueError(f'The InChI "{value}"{label} is invalid. Reason:\n{err}')
        return value

    @validator('inchi_key')
    def inchi_key_validator(cls, value, values):
        """NonPhysicalSpecies.inchi_key validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        is_valid, err = common.is_valid_inchi_key(value)
        if not is_valid:
            raise ValueError(f'The InChI Key "{value}"{label} is invalid. Reason:\n{err}')
        return value

    @validator('graph', always=True)
    def graph_validator(cls, value, values):
        """
        NonPhysicalSpecies.graph validator
        Also used to populate SMILES, InChI, InChI Key, adjlist
        """
        label = f' (non-physical-species label: "{values["label"]}")' \
            if 'label' in values and values['label'] is not None else ''
        if value is not None:
            # adjlist was given, populate other attributes as needed
            if values['smiles'] is None or values['inchi'] is None:
                smiles, inchi = converter.smiles_and_inchi_from_adjlist(value)
                values['smiles'] = values['smiles'] or smiles
                values['inchi'] = values['inchi'] or inchi
        if values['inchi'] is not None:
            # InChI was given, populate other attributes as needed
            if 'smiles' not in values or not values['smiles']:
                values['smiles'] = converter.smiles_from_inchi(values['inchi'])
            value = value or converter.adjlist_from_smiles(values['smiles'])
        if 'smiles' in values and values['smiles'] is not None:
            # SMILES was given, populate other attributes as needed
            value = value or converter.adjlist_from_smiles(values['smiles'])
            values['inchi'] = values['inchi'] or converter.inchi_from_smiles(values['smiles'])
        # populate the InChI Key if not already set
        if values['inchi_key'] is not None and values['inchi'] is None:
            # InChI Key was given (and there's no InChI), populate other attributes as needed
            values['inchi'] = converter.inchi_from_inchi_key(values['inchi_key'])
            if values['inchi'] is not None:
                values['smiles'] = values['smiles'] or converter.smiles_from_inchi(values['inchi'])
                value = value or converter.adjlist_from_smiles(values['smiles'])
        values['inchi_key'] = values['inchi_key'] or converter.inchi_key_from_inchi(values['inchi'])
        if values is None or ('smiles' in values and values['smiles'] is None) \
                or ('inchi' in values and values['inchi'] is None):
            # couldn't populate adjlist, SMILES, nor InChI
            raise ValueError(f'A species descriptor (SMILES, InChI, or graph adjacency list) must be given{label}.')
        # adjlist validation
        if value is not None:
            is_valid, err = common.is_valid_adjlist(value)
            if not is_valid:
                raise ValueError(f'The RMG adjacency list{label} is invalid:\n{value}\nReason:\n{err}')
            multiplicity = from_adjacency_list(value, group=False, saturate_h=False)[1]
            if multiplicity != values['multiplicity']:
                if not abs(values['multiplicity'] - multiplicity) % 2 + abs(values['charge']):
                    # the difference is even, so it makes sense
                    adjlist_no_multiplicity = value.split("\n", 1)[1] if 'multiplicity' in value else value
                    value = f'multiplicity {values["multiplicity"]}\n{adjlist_no_multiplicity}'
                else:
                    raise ValueError(f'The given multiplicity {values["multiplicity"]} and the multiplicity of the '
                                     f'graph adjacency list mismatch{label}:\n{value}')
        return value

    @validator('coordinates')
    def coordinates_validator(cls, value, values):
        """NonPhysicalSpecies.coordinates validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        converter.add_common_isotopes_to_coords(value)
        is_valid, err = common.is_valid_coordinates(value)
        if not is_valid:
            raise ValueError(f'The following coordinates dictionary{label} is invalid:\n{value}\nReason:\n{err}')
        return value

    @validator('fragments')
    def fragments_validator(cls, value, values):
        """NonPhysicalSpecies.fragments validator"""
        label = f' of non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        atom_indices = list()
        for fragment in value:
            for index in fragment:
                is_valid, err = common.is_valid_atom_index(index=index,
                                                           coordinates=values['coordinates'] if 'coordinates' in values
                                                           else None,
                                                           existing_indices=atom_indices)
                if not is_valid:
                    raise ValueError(f'The atom index {index} in the fragments attribute{label} is invalid. '
                                     f'Got:\n{err}.')
                atom_indices.append(index)
        if 'coordinates' in values and len(values['coordinates']['symbols']) != len(atom_indices):
            raise ValueError(f'{len(values["coordinates"]["symbols"])} atoms were specified in the fragments{label}, '
                             f'while according to its coordinates it has {len(atom_indices)} atoms.')
        value = value if len(value) > 1 else None
        return value

    @validator('fragment_orientation', always=True)
    def fragment_orientation_validator(cls, value, values):
        """NonPhysicalSpecies.fragment_orientation validator"""
        label = f' (non-physical-species label "{values["label"]}")' \
            if 'label' in values and values['label'] is not None else ''
        if value is None:
            if 'fragments' in values and values['fragments'] is not None:
                raise ValueError(f'Must specify fragment_orientation if fragments are specified{label}.')
        else:
            if 'fragments' in values:
                if values['fragments'] is None:
                    raise ValueError(f'The fragment_orientation argument{label} is unexpected if the fragments '
                                     f'argument is not specified.')
                if len(value) != len(values['fragments']) - 1:
                    raise ValueError(f'Expected {len(values["fragments"]) - 1} fragment orientation entries for a '
                                     f'species with {len(values["fragments"])} fragments, got {len(value)}.')
            valid_keys = ['cm', 'x', 'y', 'z']
            for entry in value:
                if len(list(entry.keys())) != 4:
                    raise ValueError(f'Expected the following keys in the fragment_orientation argument: "cm", "x", '
                                     f'"y", and "z". Got{label}: {list(entry.keys())}')
                for key, val in entry.items():
                    if key not in valid_keys:
                        raise ValueError(f'Got an unrecognized key "{key}" in the fragment_orientation '
                                         f'attribute{label}.')
                    if key == 'cm':
                        if not isinstance(val, list):
                            raise TypeError(f'The center of mass vector in the fragment_orientation attribute must be '
                                            f'a list type, got{label}: {type(val)}.')
                        if len(entry[key]) != 3:
                            raise ValueError(f'The center of mass vector in the fragment_orientation attribute{label} '
                                             f'has length {len(val)}, should have a length of 3.')
                    elif not isinstance(val, float):
                        raise TypeError(f'The "x", "y", and "z" in the fragment_orientation attribute must have '
                                        f'float type values, got{label}: {val} with type {type(val)} in\n{entry}.')
        return value

    @validator('chirality')
    def chirality_validator(cls, value, values):
        """NonPhysicalSpecies.chirality validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        chiral_atom_indices = list()
        allowed_values = ['R', 'S', 'NR', 'NS', 'E', 'Z']
        allowed_atoms = ['C', 'Si', 'Ge', 'Sn', 'Pb', 'N', 'P', 'As', 'Sb', 'Bi']
        for key, val in value.items():
            for index in key:
                is_valid, err = common.is_valid_atom_index(index=index,
                                                           coordinates=values['coordinates'] if 'coordinates' in values
                                                           else None,
                                                           existing_indices=chiral_atom_indices)
                if not is_valid:
                    raise ValueError(f'The atom index {index} in the fragments attribute{label} is invalid. '
                                     f'Got:\n{err}.')
                chiral_atom_indices.append(index)
                if 'coordinates' in values and values['coordinates']['symbols'][index - 1] not in allowed_atoms:
                    raise ValueError(f'A chiral site cannot include {values["coordinates"]["symbols"][index - 1]} '
                                     f'atoms. Got{label}:\n{value}')
            if val not in allowed_values:
                raise ValueError(f'The chirality notation is not recognized. Expected it to be in {allowed_values}, '
                                 f'got {val} in\n{value}')
            if len(key) == 1:
                if val not in ['R', 'S', 'NR', 'NS']:
                    raise ValueError(f'A chiral atom center must have one of the following notations: "R", "S", "NR", '
                                     f'or "NS", got {val} in {value}{label}.')
            elif len(key) == 2:
                if val not in ['E', 'Z']:
                    raise ValueError(f'A chiral center around a double bond must be noted by either "E" or "Z", '
                                     f'got {val} in {value}{label}.')
            else:
                raise ValueError(f'A chiral center must be noted by either a single atom index or two, got {len(key)} '
                                 f'in {value}{label}.')
            if val in ['NR', 'NS'] and 'coordinates' in values and values['coordinates']['symbols'][key[0] - 1] != 'N':
                raise ValueError(f'A chiral atom center{label} with an "NR" or "NS" notation but be a nitrogen atom.')
            elif val in ['R', 'S'] and 'coordinates' in values and values['coordinates']['symbols'][key[0] - 1] == 'N':
                raise ValueError(f'A chiral *nitrogen* atom center{label} with must be noted with "NR" or "NS".')
        return value

    @validator('conformation_method', always=True)
    def conformation_method_validator(cls, value, values):
        """NonPhysicalSpecies.conformation_method validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        if value is None and 'coordinates' in values and len(values['coordinates']['symbols']) >= 4:
            raise ValueError(f'Must provide a conformation method{label} when the species contains more than 4 atoms.')
        return value

    @validator('global_min_geometry')
    def global_min_geometry_validator(cls, value, values):
        """NonPhysicalSpecies.global_min_geometry validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        converter.add_common_isotopes_to_coords(value)
        is_valid, err = common.is_valid_coordinates(value)
        if not is_valid:
            raise ValueError(f'The following global_min_geometry coordinates dictionary{label} is invalid:\n'
                             f'{value}\nReason:\n{err}')
        return value

    @validator('irc_trajectories', always=True)
    def irc_trajectories_validator(cls, value, values):
        """NonPhysicalSpecies.irc_trajectories validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        if 'is_ts' in values and values['is_ts'] and value is None:
            raise ValueError(f'IRC trajectories must be given{label} if the species is a TS.')
        if value is not None:
            for i, traj in enumerate(value):
                for j, frame in enumerate(traj):
                    converter.add_common_isotopes_to_coords(frame)
                    is_valid, err = common.is_valid_coordinates(frame)
                    if not is_valid:
                        raise ValueError(f'Frame {j} in IRC trajectory {i}{label} is invalid:\n'
                                         f'{frame}\nReason:\n{err}')
        return value

    @validator('opt_path', always=True)
    def opt_path_validator(cls, value, values):
        """NonPhysicalSpecies.opt_path validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        if common.get_number_of_atoms(values) > 1 and value is None:
            raise ValueError(f'The opt_path was not given{label}.')
        return value

    @validator('freq_path', always=True)
    def freq_path_validator(cls, value, values):
        """NonPhysicalSpecies.freq_path validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        if common.get_number_of_atoms(values) > 1 and value is None:
            raise ValueError(f'The freq_path was not given{label}.')
        return value

    @validator('irc_paths', always=True)
    def irc_paths_validator(cls, value, values):
        """NonPhysicalSpecies.irc_paths validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        if 'irc_trajectories' in values and values['irc_trajectories'] and value is None:
            raise ValueError(f'The irc_paths argument was not given{label}.')
        if value is not None and len(value) not in [1, 2]:
            raise ValueError(f'The length of the IRC paths argument must be either 1 (for a forward+reverse IRC) or 2. '
                             f'Got: {len(value)}{label}.')
        return value

    @validator('unconverged_jobs')
    def unconverged_jobs_validator(cls, value, values):
        """NonPhysicalSpecies.unconverged_jobs validator"""
        label = f' for non-physical-species "{values["label"]}"' \
            if 'label' in values and values['label'] is not None else ''
        allowed_keys = ['job type', 'issue', 'troubleshooting', 'comment', 'path']
        recognized_job_types = ['opt', 'freq', 'scan', 'irc', 'sp']
        for unconverged_job in value:
            if not any(key in allowed_keys for key in unconverged_job.keys()):
                raise ValueError(f'Got an unrecognized key in unconverged_jobs{label}.\n'
                                 f'Recognized keys are: {allowed_keys}\nGot: {list(unconverged_job.keys())}')
            if 'job type' not in unconverged_job:
                raise ValueError(f'A job type is required when reporting an unconverged job. Got None{label}.`')
            else:
                if unconverged_job['job type'] not in recognized_job_types:
                    raise ValueError(f"The unconverged job type {unconverged_job['job type']}{label} is invalid.\n"
                                     f"Recognized job types are {recognized_job_types}.")
            if 'path' not in unconverged_job:
                raise ValueError(f'A file path is required when reporting an unconverged job. Got None{label}.`')
        return value


class NonPhysicalSpeciesCreate(NonPhysicalSpeciesBase):
    """Create a NonPhysicalSpecies item: Properties to receive on item creation"""
    reviewer_flags: Optional[Dict[str, str]] = None


class NonPhysicalSpeciesUpdate(NonPhysicalSpeciesBase):
    """Update a NonPhysicalSpecies item: Properties to receive on item update"""
    reviewer_flags: Optional[Dict[str, str]] = None


class NonPhysicalSpeciesInDBBase(NonPhysicalSpeciesBase):
    """Properties shared by models stored in DB"""
    id: int
    reviewer_flags: Optional[Dict[str, str]] = None

    class Config:
        orm_mode = True


class NonPhysicalSpecies(NonPhysicalSpeciesInDBBase):
    """Properties to return to client"""
    pass


class NonPhysicalSpeciesInDB(NonPhysicalSpeciesInDBBase):
    """Properties stored in DB"""
    pass

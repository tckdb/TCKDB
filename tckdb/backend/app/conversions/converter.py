"""
TCKDB backend app conversions converter module
This module is used for converting in between various species identifiers

Todo: Use the ``raise_atomtype_exception`` and ``raise_charge_exception`` arguments
      in adjlist_from_smiles() and smiles_and_inchi_from_adjlist() once RMG's binaries are updated
"""

from typing import Dict, Optional, Tuple, Union

import qcelemental as qcel

try:
    from chembl_webresource_client.unichem import UniChemClient
    from rdkit.Chem import MolFromSmiles, MolToSmiles
    from rdkit.Chem.inchi import InchiToInchiKey, MolFromInchi, MolToInchi
    from rmgpy.molecule import Molecule
except ImportError:
    # These modules are not in the requirements.txt file (cannot be installed via pip) and are skipped if not present
    pass


def inchi_from_smiles(smiles: str) -> Union[str, None]:
    """
    Get an InChI descriptor from a SMILES descriptors.
    Uses RDKit for the conversion.

    Args:
        smiles (str): The SMILES descriptor.

    Returns:
        str: The corresponding InChI descriptor.
    """
    try:
        inchi = MolToInchi(MolFromSmiles(smiles))
    except:
        return None
    return inchi


def adjlist_from_smiles(smiles: str) -> Union[str, None]:
    """
    Get an RMG adjacency list from SMILES.
    Uses RMG for the conversion.

    Args:
        smiles (str): The SMILES descriptor.

    Returns:
        str: The respective adjacency list.
    """
    try:
        mol = Molecule().from_smiles(smilesstr=smiles,
                                     raise_atomtype_exception=False)
    except:
        return None
    if mol is not None:
        adjlist = mol.to_adjacency_list()
        return adjlist
    return None


def smiles_and_inchi_from_adjlist(adjlist: str) -> Union[Tuple[str, str], Tuple[None, None]]:
    """
    Get the SMILES and InChI descriptors corresponding to an RMG adjacency list
    Uses RMG for the conversions.

    Args:
        adjlist (str): The adjacency list.

    Returns:
        Tuple[str, str]:
            - The respective SMILES.
            - The respective InChI.
    """
    try:
        mol = Molecule().from_adjacency_list(adjlist=adjlist,
                                             raise_atomtype_exception=False,
                                             raise_charge_exception=False)
    except:
        return None, None
    if mol is not None:
        smiles = mol.to_smiles()
        inchi = mol.to_inchi()
        return smiles, inchi
    return None, None


def inchi_from_inchi_key(inchi_key: str,
                         inchi_type: Optional[str] = 'standardinchi',
                         ) -> Union[str, None]:
    """
    Get an InChI descriptor from an InChI Key descriptor.
    Uses ChEMBL webresource client and 'https://www.ebi.ac.uk/unichem/'
    for the conversion.

    Note:
        This conversion is not robust and may return ``None`` even for valid InChI Keys.

    Args:
        inchi_key (str): The InChI Key descriptor.
        inchi_type (str, optional): The InChI type to return.

    Returns:
        str: The standard InChI descriptor.
    """
    uni_chem_client = UniChemClient()
    try:
        inchi = uni_chem_client.inchiFromKey(inchi_key)
    except:
        return None
    if len(inchi) and inchi_type in inchi[0]:
        return inchi[0][inchi_type]
    return None


def inchi_key_from_inchi(inchi: str) -> Union[str, None]:
    """
    Get an InChI Key descriptor from an InChI descriptor.
    Uses RDKit for the conversion.

    Args:
        inchi (str): The InChI descriptor.

    Returns:
        str: The InChI Key descriptor.
    """
    try:
        inchi_key = InchiToInchiKey(inchi)
    except:
        return None
    return inchi_key


def smiles_from_inchi(inchi: str) -> Union[str, None]:
    """
    Get a SMILES descriptor from an InChI descriptor.
    Uses RDKit for the conversion.

    Args:
        inchi (str): The InChI descriptor.

    Returns:
        str: The SMILES descriptor.
    """
    try:
        rd_mol = MolFromInchi(inchi)
        smiles = MolToSmiles(rd_mol, isomericSmiles=True, canonical=True, allBondsExplicit=False, allHsExplicit=False)
    except:
        return None
    return smiles


def add_common_isotopes_to_coords(xyz: Dict[str, Union[Tuple[Tuple[float, float, float], ...],
                                                       Tuple[int, ...], Tuple[str, ...]]]):
    """
    Add the common isotopes to the coordinates dictionary if it's missing.
    This function modifies the input dict instead of returning it.

    Args:
        xyz (dict): The coordinates dictionary
    """
    if ('isotopes' not in xyz or not xyz['isotopes']) and 'symbols' in xyz:
        xyz['isotopes'] = tuple(qcel.periodictable.to_A(symbol) for symbol in xyz['symbols'])


def str_to_xyz(xyz_str: str) -> dict:
    """
    Convert a string xyz format to the xyz dictionary style.
    The xyz string format may have optional Gaussian-style isotope information, e.g.::

        C(Iso=13)    0.6616514836    0.4027481525   -0.4847382281
        N           -0.6039793084    0.6637270105    0.0671637135
        H           -1.4226865648   -0.4973210697   -0.2238712255
        H           -0.4993010635    0.6531020442    1.0853092315
        H           -2.2115796924   -0.4529256762    0.4144516252
        H           -1.8113671395   -0.3268900681   -1.1468957003

    which will also be parsed into the xyz dictionary format, e.g.::

        {'symbols': ('C', 'N', 'H', 'H', 'H', 'H'),
         'isotopes': (13, 14, 1, 1, 1, 1),
         'coords': ((0.6616514836, 0.4027481525, -0.4847382281),
                    (-0.6039793084, 0.6637270105, 0.0671637135),
                    (-1.4226865648, -0.4973210697, -0.2238712255),
                    (-0.4993010635, 0.6531020442, 1.0853092315),
                    (-2.2115796924, -0.4529256762, 0.4144516252),
                    (-1.8113671395, -0.3268900681, -1.1468957003))}

    Args:
        xyz_str (str): The string xyz format to be converted.

    Raises:
        TypeError: If xyz_str has an incorrect type.
        ValueError: If xyz_str is unreadable.

    Returns:
        dict: The xyz dictionary format.
    """
    if not isinstance(xyz_str, str):
        raise TypeError(f'Expected a string input, got {type(xyz_str)}')
    xyz_str = xyz_str.replace(',', ' ')
    xyz_dict = {'symbols': tuple(), 'isotopes': tuple(), 'coords': tuple()}
    if all([len(line.split()) == 6 for line in xyz_str.splitlines() if line.strip()]):
        # Convert Gaussian output format, e.g., "      1          8           0        3.132319    0.769111   -0.080869"
        # not considering isotopes in this method!
        for line in xyz_str.splitlines():
            if line.strip():
                splits = line.split()
                symbol = qcel.periodictable.to_E(int(splits[1]))
                coord = (float(splits[3]), float(splits[4]), float(splits[5]))
                xyz_dict['symbols'] += (symbol,)
                xyz_dict['isotopes'] += (qcel.periodictable.to_A(symbol),)
                xyz_dict['coords'] += (coord,)
    else:
        # this is a "regular" string xyz format, if it has isotope information it will be preserved
        for line in xyz_str.strip().splitlines():
            if line.strip():
                splits = line.split()
                if len(splits) != 4:
                    raise ValueError(f'xyz_str has an incorrect format, expected 4 elements in each line, '
                                     f'got line "{line}" in:\n{xyz_str}')
                symbol = splits[0]
                if '(iso=' in symbol.lower():
                    isotope = int(symbol.split('=')[1].strip(')'))
                    symbol = symbol.split('(')[0]
                else:
                    # no specific isotope is specified in str_xyz, assume the common isotope
                    isotope = qcel.periodictable.to_A(symbol)
                coord = (float(splits[1]), float(splits[2]), float(splits[3]))
                xyz_dict['symbols'] += (symbol,)
                xyz_dict['isotopes'] += (isotope,)
                xyz_dict['coords'] += (coord,)
    return xyz_dict


def xyz_to_str(xyz_dict, isotope_format=None):
    """
    Convert an xyz dictionary format, e.g.::

        {'symbols': ('C', 'N', 'H', 'H', 'H', 'H'),
         'isotopes': (13, 14, 1, 1, 1, 1),
         'coords': ((0.6616514836, 0.4027481525, -0.4847382281),
                    (-0.6039793084, 0.6637270105, 0.0671637135),
                    (-1.4226865648, -0.4973210697, -0.2238712255),
                    (-0.4993010635, 0.6531020442, 1.0853092315),
                    (-2.2115796924, -0.4529256762, 0.4144516252),
                    (-1.8113671395, -0.3268900681, -1.1468957003))}

    to a string xyz format with optional Gaussian-style isotope specification, e.g.::

        C(Iso=13)    0.6616514836    0.4027481525   -0.4847382281
        N           -0.6039793084    0.6637270105    0.0671637135
        H           -1.4226865648   -0.4973210697   -0.2238712255
        H           -0.4993010635    0.6531020442    1.0853092315
        H           -2.2115796924   -0.4529256762    0.4144516252
        H           -1.8113671395   -0.3268900681   -1.1468957003

    Args:
        xyz_dict (dict): The ARC xyz format to be converted.
        isotope_format (str, optional): The format for specifying the isotope if it is not the most abundant one.
                                        By default, isotopes will *not* be specified. Currently the only supported
                                        option is 'gaussian'.

    Raises:
        TypeError: If xyz_dict has an incorrect type.
        ValueError: If xyz_dict is unreadable.

    Returns:
        str: The string xyz format.
    """
    if xyz_dict is None:
        return None
    recognized_isotope_formats = ['gaussian']
    if any([key not in list(xyz_dict.keys()) for key in ['symbols', 'isotopes', 'coords']]):
        raise ValueError(f'Missing keys in the xyz dictionary. Expected to find "symbols", "isotopes", and '
                         f'"coords", but got {list(xyz_dict.keys())} in\n{xyz_dict}')
    if any([len(xyz_dict['isotopes']) != len(xyz_dict['symbols']),
            len(xyz_dict['coords']) != len(xyz_dict['symbols'])]):
        raise ValueError(f'Got different lengths for "symbols", "isotopes", and "coords": '
                         f'{len(xyz_dict["symbols"])}, {len(xyz_dict["isotopes"])}, and {len(xyz_dict["coords"])}, '
                         f'respectively, in xyz:\n{xyz_dict}')
    if any([len(xyz_dict['coords'][i]) != 3 for i in range(len(xyz_dict['coords']))]):
        raise ValueError(f'Expected 3 coordinates for each atom (x, y, and z), got:\n{xyz_dict}')
    xyz_list = list()
    for symbol, isotope, coord in zip(xyz_dict['symbols'], xyz_dict['isotopes'], xyz_dict['coords']):
        common_isotope = qcel.periodictable.to_A(symbol)
        if isotope_format is not None and common_isotope != isotope:
            # consider the isotope number
            if isotope_format == 'gaussian':
                element_with_isotope = f'{symbol}(Iso={isotope})'
                row = f'{element_with_isotope:14}'
            else:
                raise ValueError(f'Recognized isotope formats for printing are {recognized_isotope_formats}, '
                                 f'got: {isotope_format}')
        else:
            # don't consider the isotope number
            row = f'{symbol:4}'
        row += '{0:14.8f}{1:14.8f}{2:14.8f}'.format(*coord)
        xyz_list.append(row)
    return '\n'.join(xyz_list)

####################################################################################################
#
# Copyright (C) Salvaire Fabrice 2015
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.  If
# not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import json
import locale
import urllib.request

from collections import OrderedDict

####################################################################################################

locale.setlocale(locale.LC_ALL, 'fr_FR')

####################################################################################################

class Field:

    ##############################################

    def __init__(self, name, factory):

        self.name = name
        self.factory = factory

####################################################################################################

def instance_checker(class_):

    def checker(obj):
        if isinstance(obj, class_):
            return obj
        else:
            raise ValueError
    
    return checker

####################################################################################################

class StringList(list):

    ##############################################

    def __init__(self, *args):

        super().__init__([str(x) for x in args])

####################################################################################################

class FromJsonMixin:

    __fields__ = ()

    ##############################################

    def __init__(self, **kwargs):

        field_names = [field.name for field in self.__fields__]
        fields = {field.name:field for field in self.__fields__}
        for key, value in kwargs.items():
            if key not in field_names:
                raise ValueError('Unknown key {}'.format(key))
            factory = fields[key].factory
            # print(key, value, factory)
            if value is not None:
                if isinstance(value, dict):
                    value = factory(**value)
                elif isinstance(value, list):
                    value = factory(*value)
                else:
                    value = factory(value)
            setattr(self, key, value)
        for key in fields:
            if key not in kwargs:
                setattr(self, key, None)

    ##############################################

    def to_json(self):

        return OrderedDict([(field.name, self.__dict__[field.name])
                            for field in self.__fields__])

####################################################################################################

class Coordonne(FromJsonMixin):

    __fields__ = (
        Field('longitude', float),
        Field('latitude', float),
    )

    ##############################################

    def __str__(self):

        return '({0.latitude}, {0.longitude})'.format(self)

####################################################################################################

class WithCoordinate(FromJsonMixin):

    ##############################################

    def to_json(self):

        d = super().to_json()
        if d['coordonne'] is not None:
            d['coordonne'] = d['coordonne'].to_json()
        
        return d

    ##############################################

    def __lt__(self, other):

        # return locale.strcoll(str(self), str(other))
        return locale.strxfrm(str(self)) < locale.strxfrm(str(other))

####################################################################################################

class Massif(WithCoordinate):

    __fields__ = (
        Field('massif', str),
        Field('coordonne', Coordonne),
        Field('type_de_chaos', str),
        Field('parcelles', str),
        Field('secteur', str),
        Field('acces', str),
        Field('itineraire', str),
        Field('velo', str),
        Field('rdv', str),
        Field('notes', str),
        Field('nom', str),
    )

    ##############################################

    def __str__(self):
        return self.massif

    ##############################################

    def str_long(self):

        template = '''
massif_id: {0.massif_id}
massif: {0.massif}
coordonné: {0.coordonne}
type_de_chaos: {0.type_de_chaos}
parcelles: {0.parcelles}
secteur: {0.secteur}
'''
        return template.format(self)

####################################################################################################

class Circuit(WithCoordinate):

    __fields__ = (
        Field('massif', instance_checker(Massif)),
        Field('couleur', str),
        Field('numero', int),
        Field('cotation', str),
        Field('topos', StringList),
        Field('coordonne', Coordonne),
        Field('annee_refection', int),
        Field('gestion', str),
        Field('status', str),
        Field('liste_blocs', StringList),
    )

    ##############################################

    def __str__(self):
        return '{0.massif}-{0.numero}'.format(self)

    ##############################################

    def str_long(self):

        template = '''
massif: {0.massif}
couleur: {0.couleur}
numéro: {0.numero}
cotation: {0.cotation}
topos: {0.topos}
coordonné: {0.coordonne}
année_réfection: {0.annee_refection}
gestion: {0.gestion}
status: {0.status}
liste_blocs: {0.liste_blocs}
'''
        return template.format(self)

    ##############################################

    def has_topo(self):

        return bool(self.topos)

    ##############################################

    def upload_topos(self):

        for url in self.topos:
            if url.endswith('.pdf'):
                print('Get', url)
                with urllib.request.urlopen(url) as response:
                    document = response.read()
                    pdf_name = url[url.rfind('/')+1:]
                    with open(pdf_name, 'wb') as f:
                        f.write(document)

    ##############################################

    def to_json(self, bleau_database):

        d = super().to_json()
        d['massif'] = str(d['massif'])
        
        return d

####################################################################################################

class BleauDataBase:

    ##############################################

    def __init__(self, json_file=None):

        if json_file is not None:
            with open(json_file, encoding='utf8') as f:
                data = json.load(f)
            massifs = [Massif(**massif_dict) for massif_dict in data['massifs']]
            self._massifs = {}
            for massif in massifs:
                self.add_massif(massif)
            self._circuits = []
            for circuit_dict in data['circuits']:
                circuit_dict['massif'] = self._massifs[circuit_dict['massif']]
                self.add_circuit(Circuit(**circuit_dict))
        else:
            self._massifs = {}
            self._circuits = []

    ##############################################

    @property
    def nombre_de_circuits(self):
        return len(self._circuits)

    @property
    def nombre_de_circuits_avec_topos(self):
        return len([circuit for circuit in self._circuits
                    if circuit.has_topo()])

    @property
    def nombre_de_massifs(self):
        return len(self._massifs)

    @property
    def massifs(self):
        return iter(sorted(self._massifs.values()))

    @property
    def circuits(self):
        return iter(sorted(self._circuits))

    ##############################################

    def __getitem__(self, key):

        return self._massifs[key]

    ##############################################

    def add_massif(self, massif):

        self._massifs[str(massif)] = massif

    ##############################################

    def add_circuit(self, circuit):

        self._circuits.append(circuit)

    ##############################################

    def to_json(self, json_file, sort_keys=False):

        data = OrderedDict(
            massifs=[massif.to_json() for massif in self.massifs],
            circuits=[circuit.to_json(self) for circuit in self.circuits],
        )
        
        with open(json_file, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=sort_keys)

####################################################################################################
#
# End
#
####################################################################################################

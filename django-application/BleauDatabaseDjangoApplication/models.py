####################################################################################################
#
# Bleau Database - A database of the bouldering area of Fontainebleau
# Copyright (C) 2016 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

# from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.db.models import (Model,
                                          ForeignKey,
                                          IntegerField,
                                          CharField, TextField,
                                          PointField)
from django.contrib.postgres.fields import JSONField

####################################################################################################

class Place(Model):

    """This class defines a place."""

    # class Meta:
    #     app_label = 'BleauDatabaseDjangoApplication'

    CATEGORIES_CHOICES = (
        (0, 'parking'),
        (1, 'gare'),
        (2, "point d'eau"),
    )

    # creation_date = models.DateTimeField(auto_now_add=True)
    category = IntegerField(choices=CATEGORIES_CHOICES)
    coordinate = PointField()
    name = CharField(max_length=100)
    note = TextField(null=True, blank=True) # aka commentaire

    ##############################################

    def __str__(self):

        return self.name

####################################################################################################

class Person(Model):

    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)

    ##############################################

    def __str__(self):

        return ' '.join((self.first_name, self.last_name))

####################################################################################################

class Massif(Model):

    """This class defines a massif."""

    acces = TextField(null=True, blank=True) # Fixme: fr
    alternative_name = CharField(max_length=100, null=True, blank=True) # Fixme
    chaos_type = CharField(max_length=3, null=True, blank=True)
    coordinate = PointField(null=True, blank=True)
    name = CharField(max_length=100)
    note = TextField(null=True, blank=True)
    parcelles = CharField(max_length=50, null=True, blank=True) # Fixme: fr
    rdv = TextField(null=True, blank=True) # Fixme: fr
    secteur = CharField(max_length=100) # Fixme: fr, entity ?
    velo = TextField(null=True, blank=True) # Fixme: fr, gare

    ##############################################

    def __str__(self):

        return self.name

####################################################################################################

class Circuit(Model):

    """This class defines a circuit."""

    boulders = JSONField(null=True, blank=True)
    colour = CharField(max_length=50, null=True, blank=True)
    coordinate = PointField(null=True, blank=True)
    creation_date = IntegerField(null=True, blank=True) # Fixme: opening ?
    gestion = CharField(max_length=50, null=True, blank=True) # Fixme: fr
    grade = CharField(max_length=3, null=True, blank=True)
    massif = ForeignKey(Massif, on_delete=models.CASCADE)
    note = TextField(null=True, blank=True)
    number = IntegerField()
    opener_string = TextField(null=True, blank=True) # Fixme: openers ? # JSONField(null=True, blank=True)
    refection_date = IntegerField(null=True, blank=True)
    refection_note = TextField(null=True, blank=True)
    status = CharField(max_length=50, null=True, blank=True)
    topos = JSONField(null=True, blank=True)

    ##############################################

    def __str__(self):
        return '{0.massif}-{0.number}'.format(self)

    ##############################################

    def openers(self):

        return self.opener_set.all()

####################################################################################################

class Opener(Model):

    circuit = models.ForeignKey(Circuit)
    person = models.ForeignKey(Person)

    ##############################################

    def __str__(self):
        return '{0.circuit}-{0.person}'.format(self)

####################################################################################################

class Refection(Model):

    circuit = models.ForeignKey(Circuit)
    date = IntegerField(null=True, blank=True)
    note = TextField(null=True, blank=True)

####################################################################################################

class RefectionPerson(Model):

    refection = models.ForeignKey(Refection)
    person = models.ForeignKey(Person)

####################################################################################################
#
# End
#
####################################################################################################

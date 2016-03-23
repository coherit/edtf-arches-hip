'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from arches.app.models.models import RelatedResource
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from arches.app.models.forms import ResourceForm
from arches.app.utils.imageutils import generate_thumbnail
from arches.app.views.concept import get_preflabel_from_valueid
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.forms.models import model_to_dict
from django.utils.translation import ugettext as _
from django.forms.models import model_to_dict
from datetime import datetime

def datetime_nodes_to_dates(branch_list):
    for branch in branch_list:
        for node in branch['nodes']:
            if isinstance(node.value, datetime):
                node.value = node.value.date()
                node.label = node.value

    return branch_list


class SummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'summary',
            'icon': 'fa-tag',
            'name': _('Resource Summary'),
            'class': SummaryForm
        }

    def update(self, data, files):
        self.update_nodes('NAME.E41', data)
        self.update_nodes('KEYWORD.E55', data)
        if self.resource.entitytypeid in ('HERITAGE_RESOURCE.E18', 'HERITAGE_RESOURCE_GROUP.E27'):   
            self.update_nodes('RESOURCE_TYPE_CLASSIFICATION.E55', data)

        beginning_of_existence_nodes = []
        end_of_existence_nodes = []
        for branch_list in data['important_dates']:
            for node in branch_list['nodes']:
                if node['entitytypeid'] == 'BEGINNING_OF_EXISTENCE_TYPE.E55':
                    beginning_of_existence_nodes.append(branch_list)
                if node['entitytypeid'] == 'END_OF_EXISTENCE_TYPE.E55':
                    end_of_existence_nodes.append(branch_list)

        for branch_list in beginning_of_existence_nodes:
            for node in branch_list['nodes']:        
                if node['entitytypeid'] == 'START_DATE_OF_EXISTENCE.E49,END_DATE_OF_EXISTENCE.E49':
                    node['entitytypeid'] = 'START_DATE_OF_EXISTENCE.E49'

        for branch_list in end_of_existence_nodes:
            for node in branch_list['nodes']:        
                if node['entitytypeid'] == 'START_DATE_OF_EXISTENCE.E49,END_DATE_OF_EXISTENCE.E49':
                    node['entitytypeid'] = 'END_DATE_OF_EXISTENCE.E49'

        self.update_nodes('BEGINNING_OF_EXISTENCE.E63', {'BEGINNING_OF_EXISTENCE.E63':beginning_of_existence_nodes})
        self.update_nodes('END_OF_EXISTENCE.E64', {'END_OF_EXISTENCE.E64':end_of_existence_nodes})

    def load(self, lang):
        self.data['important_dates'] = {
            'branch_lists': datetime_nodes_to_dates(self.get_nodes('BEGINNING_OF_EXISTENCE.E63') + self.get_nodes('END_OF_EXISTENCE.E64')),
            'domains': {'important_dates' : Concept().get_e55_domain('BEGINNING_OF_EXISTENCE_TYPE.E55') + Concept().get_e55_domain('END_OF_EXISTENCE_TYPE.E55')}
        }

        if self.resource:
            if self.resource.entitytypeid in ('HERITAGE_RESOURCE.E18', 'HERITAGE_RESOURCE_GROUP.E27'):            
                self.data['RESOURCE_TYPE_CLASSIFICATION.E55'] = {
                    'branch_lists': self.get_nodes('RESOURCE_TYPE_CLASSIFICATION.E55'),
                    'domains': {'RESOURCE_TYPE_CLASSIFICATION.E55' : Concept().get_e55_domain('RESOURCE_TYPE_CLASSIFICATION.E55')}
                }

            self.data['NAME.E41'] = {
                'branch_lists': self.get_nodes('NAME.E41'),
                'domains': {'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')}
                # 'defaults': {
                #     'NAME_TYPE.E55': default_name_type['id'],
                #     'NAME.E41': ''
                # }
            }

            self.data['KEYWORD.E55'] = {
                'branch_lists': self.get_nodes('KEYWORD.E55'),
                'domains': {'KEYWORD.E55' : Concept().get_e55_domain('KEYWORD.E55')}
            }

            try:
                self.data['primaryname_conceptid'] = self.data['NAME.E41']['domains']['NAME_TYPE.E55'][3]['id']
            except IndexError:
                pass

class ExternalReferenceForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'external-reference',
            'icon': 'fa-random',
            'name': _('External System References'),
            'class': ExternalReferenceForm
        }

    def update(self, data, files):
        self.update_nodes('EXTERNAL_RESOURCE.E1', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['EXTERNAL_RESOURCE.E1'] = {
                'branch_lists': self.get_nodes('EXTERNAL_RESOURCE.E1'),
                'domains': {
                    'EXTERNAL_XREF_TYPE.E55': Concept().get_e55_domain('EXTERNAL_XREF_TYPE.E55'),
                }
            }

class ActivityActionsForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'activity-actions',
            'icon': 'fa-flash',
            'name': _('Actions'),
            'class': ActivityActionsForm
        }

    def update(self, data, files):
        self.update_nodes('PHASE_TYPE_ASSIGNMENT.E17', data)
        return

    def load(self, lang):

        if self.resource:
            phase_type_nodes = datetime_nodes_to_dates(self.get_nodes('PHASE_TYPE_ASSIGNMENT.E17'))

            self.data['PHASE_TYPE_ASSIGNMENT.E17'] = {
                'branch_lists': phase_type_nodes,
                'domains': {
                    'ACTIVITY_TYPE.E55': Concept().get_e55_domain('ACTIVITY_TYPE.E55'),
                }
            }

class ActivitySummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'activity-summary',
            'icon': 'fa-tag',
            'name': _('Resource Summary'),
            'class': ActivitySummaryForm
        }

    def update(self, data, files):
        self.update_nodes('NAME.E41', data)
        self.update_nodes('KEYWORD.E55', data)
        self.update_nodes('BEGINNING_OF_EXISTENCE.E63', data)
        self.update_nodes('END_OF_EXISTENCE.E64', data)

    def load(self, lang):
        if self.resource:

            self.data['NAME.E41'] = {
                'branch_lists': self.get_nodes('NAME.E41'),
                'domains': {'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')}
            }

            self.data['KEYWORD.E55'] = {
                'branch_lists': self.get_nodes('KEYWORD.E55'),
                'domains': {'KEYWORD.E55' : Concept().get_e55_domain('KEYWORD.E55')}
            }

            self.data['BEGINNING_OF_EXISTENCE.E63'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('BEGINNING_OF_EXISTENCE.E63')),
                'domains': {
                    'BEGINNING_OF_EXISTENCE_TYPE.E55' : Concept().get_e55_domain('BEGINNING_OF_EXISTENCE_TYPE.E55')
                }
            }

            self.data['END_OF_EXISTENCE.E64'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('END_OF_EXISTENCE.E64')),
                'domains': {
                    'END_OF_EXISTENCE_TYPE.E55' : Concept().get_e55_domain('END_OF_EXISTENCE_TYPE.E55')
                }
            }
            try:
                self.data['primaryname_conceptid'] = self.data['NAME.E41']['domains']['NAME_TYPE.E55'][3]['id']
            except IndexError:
                pass


class ComponentForm(ResourceForm):
    baseentity = None

    @staticmethod
    def get_info():
        return {
            'id': 'component',
            'icon': 'fa fa-bar-chart-o',
            'name': _('Components'),
            'class': ComponentForm
        }

    def update(self, data, files):
        self.update_nodes('COMPONENT.E18', data)
        self.update_nodes('MODIFICATION_EVENT.E11', data)
        return

    def update_nodes(self, entitytypeid, data):

        self.resource.prune(entitytypes=[entitytypeid])

        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        for value in data[entitytypeid]:
            self.baseentity = None
            for newentity in value['nodes']:
                entity = Entity()
                entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                if self.baseentity == None:
                    self.baseentity = entity
                else:
                    self.baseentity.merge(entity)
            
            if entitytypeid == 'COMPONENT.E18':

                production_entities = self.resource.find_entities_by_type_id('PRODUCTION.E12')

                if len(production_entities) > 0:
                    self.resource.merge_at(self.baseentity, 'PRODUCTION.E12')
                else:
                    self.resource.merge_at(self.baseentity, self.resource.entitytypeid)

            else:
                self.resource.merge_at(self.baseentity, self.resource.entitytypeid)

        self.resource.trim()

    def load(self, lang):
        if self.resource:

            self.data['COMPONENT.E18'] = {
                'branch_lists': self.get_nodes('COMPONENT.E18'),
                'domains': {
                    'CONSTRUCTION_TECHNIQUE.E55': Concept().get_e55_domain('CONSTRUCTION_TECHNIQUE.E55'),
                    'MATERIAL.E57' : Concept().get_e55_domain('MATERIAL.E57'),
                    'COMPONENT_TYPE.E55' : Concept().get_e55_domain('COMPONENT_TYPE.E55')
                }
            }
            self.data['MODIFICATION_EVENT.E11'] = {
                'branch_lists': self.get_nodes('MODIFICATION_EVENT.E11'),
                'domains': {
                    'MODIFICATION_TYPE.E55': Concept().get_e55_domain('MODIFICATION_TYPE.E55'),
                }
            }


class ClassificationForm(ResourceForm):
    baseentity = None

    @staticmethod
    def get_info():
        return {
            'id': 'classification',
            'icon': 'fa-adjust',
            'name': _('Classifications'),
            'class': ClassificationForm
        }

    def get_nodes(self, entity, entitytypeid):
        ret = []
        entities = entity.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            ret.append({'nodes': entity.flatten()})

        return ret

    def update_nodes(self, entitytypeid, data):
        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        for value in data[entitytypeid]:
            for newentity in value['nodes']:
                entity = Entity()
                entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                if self.baseentity == None:
                    self.baseentity = entity
                else:
                    self.baseentity.merge(entity)

    def update(self, data, files):

        self.update_nodes('HERITAGE_RESOURCE_TYPE.E55', data)
        self.update_nodes('TO_DATE.E49', data)
        self.update_nodes('FROM_DATE.E49', data)
        self.update_nodes('HERITAGE_RESOURCE_USE_TYPE.E55', data)
        self.update_nodes('CULTURAL_PERIOD.E55', data)
        self.update_nodes('STYLE.E55', data)
        self.update_nodes('ANCILLARY_FEATURE_TYPE.E55', data)
        production_entities = self.resource.find_entities_by_type_id('PRODUCTION.E12')

        phase_type_node_id = ''
        for value in data['PHASE_TYPE_ASSIGNMENT.E17']:
            for node in value['nodes']:
                if node['entitytypeid'] == 'PHASE_TYPE_ASSIGNMENT.E17' and node['entityid'] != '':
                    #remove the node
                    phase_type_node_id = node['entityid']
                    self.resource.filter(lambda entity: entity.entityid != node['entityid'])

        for entity in self.baseentity.find_entities_by_type_id('PHASE_TYPE_ASSIGNMENT.E17'):
            entity.entityid = phase_type_node_id

        if len(production_entities) > 0:
            self.resource.merge_at(self.baseentity, 'PRODUCTION.E12')
        else:
            self.resource.merge_at(self.baseentity, self.resource.entitytypeid)

        self.resource.trim()
                   
    def load(self, lang):

        self.data = {
            'data': [],
            'domains': {
                'HERITAGE_RESOURCE_TYPE.E55': Concept().get_e55_domain('HERITAGE_RESOURCE_TYPE.E55'),
                'HERITAGE_RESOURCE_USE_TYPE.E55' : Concept().get_e55_domain('HERITAGE_RESOURCE_USE_TYPE.E55'),
                'CULTURAL_PERIOD.E55' : Concept().get_e55_domain('CULTURAL_PERIOD.E55'),
                'STYLE.E55' : Concept().get_e55_domain('STYLE.E55'),
                'ANCILLARY_FEATURE_TYPE.E55' : Concept().get_e55_domain('ANCILLARY_FEATURE_TYPE.E55')
            }
        }

        classification_entities = self.resource.find_entities_by_type_id('PHASE_TYPE_ASSIGNMENT.E17')

        for entity in classification_entities:
            to_date_nodes = datetime_nodes_to_dates(self.get_nodes(entity, 'TO_DATE.E49'))
            from_date_nodes = datetime_nodes_to_dates(self.get_nodes(entity, 'FROM_DATE.E49'))

            self.data['data'].append({
                'HERITAGE_RESOURCE_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'HERITAGE_RESOURCE_TYPE.E55')
                },
                'HERITAGE_RESOURCE_USE_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'HERITAGE_RESOURCE_USE_TYPE.E55')
                },
                'CULTURAL_PERIOD.E55': {
                    'branch_lists': self.get_nodes(entity, 'CULTURAL_PERIOD.E55')
                },
                'TO_DATE.E49': {
                    'branch_lists': to_date_nodes
                },
                'FROM_DATE.E49': {
                    'branch_lists': from_date_nodes
                },
                'STYLE.E55': {
                    'branch_lists': self.get_nodes(entity, 'STYLE.E55')
                },
                'ANCILLARY_FEATURE_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'ANCILLARY_FEATURE_TYPE.E55')
                },
                'PHASE_TYPE_ASSIGNMENT.E17': {
                    'branch_lists': self.get_nodes(entity, 'PHASE_TYPE_ASSIGNMENT.E17')
                }
            })
           

class HistoricalEventSummaryForm(ActivitySummaryForm):
    @staticmethod
    def get_info():
        return {
            'id': 'historical-event-summary',
            'icon': 'fa-tag',
            'name': _('Resource Summary'),
            'class': HistoricalEventSummaryForm
        }    

class InformationResourceSummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'information-resource-summary',
            'icon': 'fa-tag',
            'name': _('Resource Summary'),
            'class': InformationResourceSummaryForm
        }   

    def update(self, data, files):
        self.update_nodes('TITLE.E41', data)
        self.update_nodes('IDENTIFIER.E42', data)
        self.update_nodes('KEYWORD.E55', data)
        self.update_nodes('INFORMATION_CARRIER.E84', data)
        self.update_nodes('LANGUAGE.E55', data)

    def load(self, lang):
        if self.resource:

            self.data['TITLE.E41'] = {
                'branch_lists': self.get_nodes('TITLE.E41'),
                'domains': {'TITLE_TYPE.E55' : Concept().get_e55_domain('TITLE_TYPE.E55')}
            }

            self.data['IDENTIFIER.E42'] = {
                'branch_lists': self.get_nodes('IDENTIFIER.E42'),
                'domains': {
                    'IDENTIFIER_TYPE.E55' : Concept().get_e55_domain('IDENTIFIER_TYPE.E55')
                }
            }

            self.data['INFORMATION_CARRIER.E84'] = {
                'branch_lists': self.get_nodes('INFORMATION_CARRIER.E84'),
                'domains': {
                    'INFORMATION_CARRIER_FORMAT_TYPE.E55' : Concept().get_e55_domain('INFORMATION_CARRIER_FORMAT_TYPE.E55')
                }
            }

            self.data['LANGUAGE.E55'] = {
                'branch_lists': self.get_nodes('LANGUAGE.E55'),
                'domains': {'LANGUAGE.E55' : Concept().get_e55_domain('LANGUAGE.E55')}
            }

            self.data['KEYWORD.E55'] = {
                'branch_lists': self.get_nodes('KEYWORD.E55'),
                'domains': {'KEYWORD.E55' : Concept().get_e55_domain('KEYWORD.E55')}
            }

            # self.data['primaryname_conceptid'] = self.data['TITLE.E41']['domains']['TITLE_TYPE.E55'][3]['id']
 

class DescriptionForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'description',
            'icon': 'fa-picture-o',
            'name': _('Descriptions'),
            'class': DescriptionForm
        }

    def update(self, data, files):
        self.update_nodes('DESCRIPTION.E62', data)

    def load(self, lang):
        description_types = Concept().get_e55_domain('DESCRIPTION_TYPE.E55')
        try:
            default_description_type = description_types[2]
            if self.resource:
                self.data['DESCRIPTION.E62'] = {
                    'branch_lists': self.get_nodes('DESCRIPTION.E62'),
                    'domains': {'DESCRIPTION_TYPE.E55' : description_types},
                    'defaults': {
                        'DESCRIPTION_TYPE.E55': default_description_type['id'],
                    }
                }
        except IndexError:
            pass


class MeasurementForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'measurement',
            'icon': 'fa-th-large',
            'name': _('Measurements'),
            'class': MeasurementForm
        }

    def update(self, data, files):
        self.update_nodes('MEASUREMENT_TYPE.E55', data)


    def load(self, lang):
        if self.resource:
            self.data['MEASUREMENT_TYPE.E55'] = {
                'branch_lists': self.get_nodes('MEASUREMENT_TYPE.E55'),
                'domains': {
                    'MEASUREMENT_TYPE.E55' : Concept().get_e55_domain('MEASUREMENT_TYPE.E55'),
                    'UNIT_OF_MEASUREMENT.E55': Concept().get_e55_domain('UNIT_OF_MEASUREMENT.E55')
                }
            }

class ConditionForm(ResourceForm):
    baseentity = None

    @staticmethod
    def get_info():
        return {
            'id': 'condition',
            'icon': 'fa-asterisk',
            'name': _('Condition Assessment'),
            'class': ConditionForm
        }

    def get_nodes(self, entity, entitytypeid):
        ret = []
        entities = entity.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            ret.append({'nodes': entity.flatten()})

        return ret

    def update_nodes(self, entitytypeid, data):
        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)

        for value in data[entitytypeid]:
            if entitytypeid == 'CONDITION_IMAGE.E73':
                temp = None
                for newentity in value['nodes']:
                    if newentity['entitytypeid'] != 'CONDITION_IMAGE.E73':
                        entity = Entity()
                        entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                        if temp == None:
                            temp = entity
                        else:
                            temp.merge(entity)

                self.baseentity.merge_at(temp, 'CONDITION_STATE.E3')
            else:
                for newentity in value['nodes']:
                    entity = Entity()
                    entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                    if self.baseentity == None:
                        self.baseentity = entity
                    else:
                        self.baseentity.merge(entity)

    def update(self, data, files):
        if len(files) > 0:
            for f in files:
                data['CONDITION_IMAGE.E73'].append({
                    'nodes':[{
                        'entitytypeid': 'CONDITION_IMAGE_FILE_PATH.E62',
                        'entityid': '',
                        'value': files[f]
                    },{
                        'entitytypeid': 'CONDITION_IMAGE_THUMBNAIL.E62',
                        'entityid': '',
                        'value': generate_thumbnail(files[f])
                    }]
                })

        for value in data['CONDITION_ASSESSMENT.E14']:
            for node in value['nodes']:
                if node['entitytypeid'] == 'CONDITION_ASSESSMENT.E14' and node['entityid'] != '':
                    #remove the node
                    self.resource.filter(lambda entity: entity.entityid != node['entityid'])

        self.update_nodes('CONDITION_TYPE.E55', data)
        self.update_nodes('THREAT_TYPE.E55', data)
        self.update_nodes('RECOMMENDATION_TYPE.E55', data)
        self.update_nodes('DATE_CONDITION_ASSESSED.E49', data)
        self.update_nodes('CONDITION_DESCRIPTION.E62', data)
        self.update_nodes('DISTURBANCE_TYPE.E55', data)
        self.update_nodes('CONDITION_IMAGE.E73', data)
        self.resource.merge_at(self.baseentity, self.resource.entitytypeid)
        self.resource.trim()
                   
    def load(self, lang):

        self.data = {
            'data': [],
            'domains': {
                'DISTURBANCE_TYPE.E55': Concept().get_e55_domain('DISTURBANCE_TYPE.E55'),
                'CONDITION_TYPE.E55' : Concept().get_e55_domain('CONDITION_TYPE.E55'),
                'THREAT_TYPE.E55' : Concept().get_e55_domain('THREAT_TYPE.E55'),
                'RECOMMENDATION_TYPE.E55' : Concept().get_e55_domain('RECOMMENDATION_TYPE.E55')
            }
        }

        condition_assessment_entities = self.resource.find_entities_by_type_id('CONDITION_ASSESSMENT.E14')

        for entity in condition_assessment_entities:
            self.data['data'].append({
                'DISTURBANCE_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'DISTURBANCE_TYPE.E55')
                },
                'CONDITION_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'CONDITION_TYPE.E55')
                },
                'THREAT_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'THREAT_TYPE.E55')
                },
                'RECOMMENDATION_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'RECOMMENDATION_TYPE.E55')
                },
                'DATE_CONDITION_ASSESSED.E49': {
                    'branch_lists': datetime_nodes_to_dates(self.get_nodes(entity, 'DATE_CONDITION_ASSESSED.E49'))
                },
                'CONDITION_DESCRIPTION.E62': {
                    'branch_lists': self.get_nodes(entity, 'CONDITION_DESCRIPTION.E62')
                },
                'CONDITION_IMAGE.E73': {
                    'branch_lists': self.get_nodes(entity, 'CONDITION_IMAGE.E73')
                },
                'CONDITION_ASSESSMENT.E14': {
                    'branch_lists': self.get_nodes(entity, 'CONDITION_ASSESSMENT.E14')
                }
            })


class LocationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'location',
            'icon': 'fa-map-marker',
            'name': _('Location'),
            'class': LocationForm
        }

    def update(self, data, files):
        if self.resource.entitytypeid not in ['ACTOR.E39']:
            self.update_nodes('SPATIAL_COORDINATES_GEOMETRY.E47', data)
            self.update_nodes('ADMINISTRATIVE_SUBDIVISION.E48', data)
        if self.resource.entitytypeid not in ['ACTOR.E39', 'ACTIVITY.E7', 'HISTORICAL_EVENT.E5']:
            self.update_nodes('PLACE_APPELLATION_CADASTRAL_REFERENCE.E44', data)
        if self.resource.entitytypeid not in ['ACTOR.E39', 'ACTIVITY.E7', 'HERITAGE_RESOURCE_GROUP.E27', 'HISTORICAL_EVENT.E5']:
            self.update_nodes('SETTING_TYPE.E55', data)
        self.update_nodes('PLACE_ADDRESS.E45', data)
        self.update_nodes('DESCRIPTION_OF_LOCATION.E62', data)
        return

    def load(self, lang):
        self.data['SPATIAL_COORDINATES_GEOMETRY.E47'] = {
            'branch_lists': self.get_nodes('SPATIAL_COORDINATES_GEOMETRY.E47'),
            'domains': {
                'GEOMETRY_QUALIFIER.E55': Concept().get_e55_domain('GEOMETRY_QUALIFIER.E55')
            }
        }

        self.data['PLACE_ADDRESS.E45'] = {
            'branch_lists': self.get_nodes('PLACE_ADDRESS.E45'),
            'domains': {
                'ADDRESS_TYPE.E55': Concept().get_e55_domain('ADDRESS_TYPE.E55')
            }
        }
        
        self.data['DESCRIPTION_OF_LOCATION.E62'] = {
            'branch_lists': self.get_nodes('DESCRIPTION_OF_LOCATION.E62'),
            'domains': {}
        }

        self.data['SETTING_TYPE.E55'] = {
            'branch_lists': self.get_nodes('SETTING_TYPE.E55'),
            'domains': {
                'SETTING_TYPE.E55': Concept().get_e55_domain('SETTING_TYPE.E55')
            }
        }

        self.data['ADMINISTRATIVE_SUBDIVISION.E48'] = {
            'branch_lists': self.get_nodes('ADMINISTRATIVE_SUBDIVISION.E48'),
            'domains': {
                'ADMINISTRATIVE_SUBDIVISION_TYPE.E55': Concept().get_e55_domain('ADMINISTRATIVE_SUBDIVISION_TYPE.E55')
            }
        }

        self.data['PLACE_APPELLATION_CADASTRAL_REFERENCE.E44'] = {
            'branch_lists': self.get_nodes('PLACE_APPELLATION_CADASTRAL_REFERENCE.E44'),
            'domains': {}
        }

        return


class CoverageForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'coverage',
            'icon': 'fa-crosshairs',
            'name': _('Coverage'),
            'class': CoverageForm
        }

    def update(self, data, files):
        self.update_nodes('SPATIAL_COORDINATES_GEOMETRY.E47', data)    
        self.update_nodes('DESCRIPTION_OF_LOCATION.E62', data)
        self.update_nodes('TEMPORAL_COVERAGE_TIME-SPAN.E52', data)
        return

    def load(self, lang):
        self.data['SPATIAL_COORDINATES_GEOMETRY.E47'] = {
            'branch_lists': self.get_nodes('SPATIAL_COORDINATES_GEOMETRY.E47'),
            'domains': {
                'GEOMETRY_QUALIFIER.E55': Concept().get_e55_domain('GEOMETRY_QUALIFIER.E55')
            }
        }
        
        self.data['DESCRIPTION_OF_LOCATION.E62'] = {
            'branch_lists': self.get_nodes('DESCRIPTION_OF_LOCATION.E62'),
            'domains': {}
        }

        self.data['TEMPORAL_COVERAGE_TIME-SPAN.E52'] = {
            'branch_lists': self.get_nodes('TEMPORAL_COVERAGE_TIME-SPAN.E52'),
            'domains': {}
        }

        return


class RelatedFilesForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'related-files',
            'icon': 'fa-file-text-o',
            'name': _('Images and Files'),
            'class': RelatedFilesForm
        }

    def update(self, data, files):
        filedict = {}
        se = SearchEngineFactory().create()

        for name in files:
            for f in files.getlist(name):
                filedict[f.name] = f

        for newfile in data.get('new-files', []):
            resource = Resource()
            resource.entitytypeid = 'INFORMATION_RESOURCE.E73'

            resource.set_entity_value('TITLE_TYPE.E55', newfile['title_type']['value'])
            resource.set_entity_value('TITLE.E41', newfile['title'])
            if newfile.get('description') and len(newfile.get('description')) > 0:
                resource.set_entity_value('DESCRIPTION_TYPE.E55', newfile['description_type']['value'])
                resource.set_entity_value('DESCRIPTION.E62', newfile.get('description'))

            resource.set_entity_value('FILE_PATH.E62', filedict[newfile['id']])
            thumbnail = generate_thumbnail(filedict[newfile['id']])
            if thumbnail != None:
                resource.set_entity_value('THUMBNAIL.E62', thumbnail)
            resource.save()
            resource.index()

            if self.resource.entityid == '':
                self.resource.save()
            relationship = self.resource.create_resource_relationship(resource.entityid, relationship_type_id=newfile['relationshiptype']['value'])
            se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')


        edited_file = data.get('current-files', None)
        if edited_file:
            title = ''
            title_type = ''
            description = ''
            description_type = ''
            for node in edited_file.get('nodes'):
                if node['entitytypeid'] == 'TITLE.E41':
                    title = node.get('value')
                elif node['entitytypeid'] == 'TITLE_TYPE.E55':
                    title_type = node.get('value')
                elif node['entitytypeid'] == 'DESCRIPTION.E62':
                    description = node.get('value')
                elif node['entitytypeid'] == 'DESCRIPTION_TYPE.E55':
                    description_type = node.get('value')
                elif node['entitytypeid'] == 'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55':
                    resourcexid = node.get('resourcexid')            
                    entityid1 = node.get('entityid1')
                    entityid2 = node.get('entityid2')
                    relationship = RelatedResource.objects.get(pk=resourcexid)
                    relationship.relationshiptype = node.get('value')
                    relationship.save()
                    se.delete(index='resource_relations', doc_type='all', id=resourcexid)
                    se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')

            relatedresourceid = entityid2 if self.resource.entityid == entityid1 else entityid1
            relatedresource = Resource().get(relatedresourceid)
            relatedresource.set_entity_value('TITLE_TYPE.E55', title_type)
            relatedresource.set_entity_value('TITLE.E41', title)
            if description != '':
                relatedresource.set_entity_value('DESCRIPTION_TYPE.E55', description_type)
                relatedresource.set_entity_value('DESCRIPTION.E62', description)
            relatedresource.save()
            relatedresource.index()

        return

    def load(self, lang):
        data = []
        for relatedentity in self.resource.get_related_resources(entitytypeid='INFORMATION_RESOURCE.E73'):
            nodes = relatedentity['related_entity'].flatten()
            dummy_relationship_entity = model_to_dict(relatedentity['relationship'])
            dummy_relationship_entity['entitytypeid'] = 'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55'
            dummy_relationship_entity['value'] = dummy_relationship_entity['relationshiptype']
            dummy_relationship_entity['label'] = ''
            nodes.append(dummy_relationship_entity)
            data.append({'nodes': nodes, 'relationshiptypelabel': get_preflabel_from_valueid(relatedentity['relationship'].relationshiptype, lang)['value']})

        self.data['current-files'] = {
            'branch_lists': data,
            'domains': {
                'RELATIONSHIP_TYPES.E32': Concept().get_e55_domain('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55'),
                'TITLE_TYPE.E55': Concept().get_e55_domain('TITLE_TYPE.E55'),
                'DESCRIPTION_TYPE.E55': Concept().get_e55_domain('DESCRIPTION_TYPE.E55')
            }
        }

        return


class FileUploadForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'file-upload',
            'icon': 'fa-file-text-o',
            'name': _('File Upload'),
            'class': FileUploadForm
        }

    def update(self, data, files):
        self.resource.prune(entitytypes=['FILE_PATH.E62', 'THUMBNAIL.E62'])
        self.resource.trim()

        if files:
            for key, value in files.items():
                self.resource.set_entity_value('FILE_PATH.E62', value)
                thumbnail = generate_thumbnail(value)
                if thumbnail != None:
                    self.resource.set_entity_value('THUMBNAIL.E62', thumbnail)
        return


    def load(self, lang):
        if self.resource:
            self.data['INFORMATION_RESOURCE.E73'] = {
                'branch_lists': self.get_nodes('INFORMATION_RESOURCE.E73'),
                'is_image': is_image(self.resource)
            }

        return   

def is_image(resource):
    for format_type in resource.find_entities_by_type_id('INFORMATION_CARRIER_FORMAT_TYPE.E55'):
        concept = Concept().get(id=format_type['conceptid'], include=['undefined'])
        for value in concept.values:
            if value.value == 'Y' and value.type == 'ViewableInBrowser':
                return True
    return False


class DesignationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'designation',
            'icon': 'fa-shield',
            'name': _('Designation'),
            'class': DesignationForm
        }

    def update(self, data, files):
        self.update_nodes('PROTECTION_EVENT.E65', data)
        return


    def load(self, lang):
        if self.resource:
            self.data['PROTECTION_EVENT.E65'] = {
                'branch_lists': self.get_nodes('PROTECTION_EVENT.E65'),
                'domains': {
                    'TYPE_OF_DESIGNATION_OR_PROTECTION.E55' : Concept().get_e55_domain('TYPE_OF_DESIGNATION_OR_PROTECTION.E55')
                }
            }

        return

class RoleForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'roles',
            'icon': 'fa-flash',
            'name': _('Role'),
            'class': RoleForm
        }

    def update(self, data, files):
        self.update_nodes('PHASE_TYPE_ASSIGNMENT.E17', data)
        return


    def load(self, lang):
        if self.resource:
            self.data['PHASE_TYPE_ASSIGNMENT.E17'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('PHASE_TYPE_ASSIGNMENT.E17')),
                'domains': {
                    'ACTOR_TYPE.E55' : Concept().get_e55_domain('ACTOR_TYPE.E55'),
                    'CULTURAL_PERIOD.E55' : Concept().get_e55_domain('CULTURAL_PERIOD.E55')
                }
            }

        return

class ActorSummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'actor-summary',
            'icon': 'fa-tag',
            'name': _('Actor Summary'),
            'class': ActorSummaryForm
        }

    def update(self, data, files):
        self.update_nodes('APPELLATION.E41', data)
        self.update_nodes('EPITHET.E82', data)
        self.update_nodes('BEGINNING_OF_EXISTENCE.E63', data)
        self.update_nodes('END_OF_EXISTENCE.E64', data)
        self.update_nodes('KEYWORD.E55', data)

    def load(self, lang):
        if self.resource:
            self.data['APPELLATION.E41'] = {
                'branch_lists': self.get_nodes('APPELLATION.E41'),
                'domains': {
                    'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')
                }
            }

            self.data['EPITHET.E82'] = {
                'branch_lists': self.get_nodes('EPITHET.E82'),
            }


            self.data['BEGINNING_OF_EXISTENCE.E63'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('BEGINNING_OF_EXISTENCE.E63')),
                'domains': {
                    'BEGINNING_OF_EXISTENCE_TYPE.E55' : Concept().get_e55_domain('BEGINNING_OF_EXISTENCE_TYPE.E55')
                }
            }

            self.data['END_OF_EXISTENCE.E64'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('END_OF_EXISTENCE.E64')),
                'domains': {
                    'END_OF_EXISTENCE_TYPE.E55' : Concept().get_e55_domain('END_OF_EXISTENCE_TYPE.E55')
                }
            }

            self.data['KEYWORD.E55'] = {
                'branch_lists': self.get_nodes('KEYWORD.E55'),
                'domains': {
                    'KEYWORD.E55' : Concept().get_e55_domain('KEYWORD.E55')}
            }
            try:
                self.data['primaryname_conceptid'] = self.data['APPELLATION.E41']['domains']['NAME_TYPE.E55'][3]['id']
            except IndexError:
                pass


class PhaseForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'phase',
            'icon': 'fa-flash',
            'name': _('Phase'),
            'class': PhaseForm
        }

    def update(self, data, files):
        self.update_nodes('PHASE_TYPE_ASSIGNMENT.E17', data)
        return


    def load(self, lang):
        if self.resource:
            self.data['PHASE_TYPE_ASSIGNMENT.E17'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('PHASE_TYPE_ASSIGNMENT.E17')),
                'domains': {
                    'HISTORICAL_EVENT_TYPE.E55' : Concept().get_e55_domain('HISTORICAL_EVENT_TYPE.E55'),
                    'CULTURAL_PERIOD.E55' : Concept().get_e55_domain('CULTURAL_PERIOD.E55')
                }
            }

        return


class EvaluationForm(ResourceForm):
    baseentity = None

    @staticmethod
    def get_info():
        return {
            'id': 'evaluation',
            'icon': 'fa-star-half-o',
            'name': _('Evaluation Criteria'),
            'class': EvaluationForm
        }

    def get_nodes(self, entity, entitytypeid):
        ret = []
        entities = entity.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            ret.append({'nodes': entity.flatten()})

        return ret

    def update_nodes(self, entitytypeid, data):
        # self.resource.prune(entitytypes=[entitytypeid])
        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)

        for value in data[entitytypeid]:
            for newentity in value['nodes']:
                entity = Entity()
                entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                if self.baseentity == None:
                    self.baseentity = entity
                else:
                    self.baseentity.merge(entity)

        # self.resource.trim()



    def update(self, data, files):
        for value in data['EVALUATION_CRITERIA_ASSIGNMENT.E13']:
            for node in value['nodes']:
                if node['entitytypeid'] == 'EVALUATION_CRITERIA_ASSIGNMENT.E13' and node['entityid'] != '':
                    #remove the node
                    self.resource.filter(lambda entity: entity.entityid != node['entityid'])

        self.update_nodes('STATUS.E55', data)
        self.update_nodes('EVALUATION_CRITERIA_TYPE.E55', data)
        self.update_nodes('ELIGIBILITY_REQUIREMENT_TYPE.E55', data)
        self.update_nodes('INTEGRITY_TYPE.E55', data)
        self.update_nodes('REASONS.E62', data)
        self.update_nodes('DATE_EVALUATED.E49', data)

        self.resource.merge_at(self.baseentity, self.resource.entitytypeid)
        self.resource.trim()



    def load(self, lang):

        self.data = {
            'data': [],
            'domains': {
                'STATUS.E55': Concept().get_e55_domain('STATUS.E55'),
                'EVALUATION_CRITERIA_TYPE.E55' : Concept().get_e55_domain('EVALUATION_CRITERIA_TYPE.E55'),
                'INTEGRITY_TYPE.E55' : Concept().get_e55_domain('INTEGRITY_TYPE.E55'),
                'ELIGIBILITY_REQUIREMENT_TYPE.E55' : Concept().get_e55_domain('ELIGIBILITY_REQUIREMENT_TYPE.E55')
            }
        }

        evaluation_assessment_entities = self.resource.find_entities_by_type_id('EVALUATION_CRITERIA_ASSIGNMENT.E13')

        for entity in evaluation_assessment_entities:
            self.data['data'].append({
                'STATUS.E55': {
                    'branch_lists': self.get_nodes(entity, 'STATUS.E55')
                },
                'EVALUATION_CRITERIA_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'EVALUATION_CRITERIA_TYPE.E55')
                },
                'INTEGRITY_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'INTEGRITY_TYPE.E55')
                },
                'ELIGIBILITY_REQUIREMENT_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'ELIGIBILITY_REQUIREMENT_TYPE.E55')
                },
                'REASONS.E62': {
                    'branch_lists': self.get_nodes(entity, 'REASONS.E62')
                },
                'EVALUATION_CRITERIA_ASSIGNMENT.E13': {
                    'branch_lists': self.get_nodes(entity, 'EVALUATION_CRITERIA_ASSIGNMENT.E13')
                },
                'DATE_EVALUATED.E49': {
                    'branch_lists': self.get_nodes(entity, 'DATE_EVALUATED.E49')
                }
            })

class RelatedResourcesForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'related-resources',
            'icon': 'fa-exchange',
            'name': _('Related Resources'),
            'class': RelatedResourcesForm
        }

    def update(self, data, files):
        se = SearchEngineFactory().create()
        related_resources_data = data.get('related-resources', [])
        original_relations = self.resource.get_related_resources()
        if self.resource.entityid == '':
            self.resource.save()
        relationship_ids = []

        for related_resource in related_resources_data:
            relationship_id = related_resource['relationship']['resourcexid']
            relationship_ids.append(relationship_id)
            resource_id = related_resource['relatedresourceid']
            relationship_type_id = related_resource['relationship']['relationshiptype']
            if isinstance(relationship_type_id, dict):
                relationship_type_id = relationship_type_id['value']
            notes = related_resource['relationship']['notes']
            date_started = related_resource['relationship']['datestarted']
            date_ended = related_resource['relationship']['dateended']
            if not relationship_id:
                relationship = self.resource.create_resource_relationship(resource_id, relationship_type_id=relationship_type_id, notes=notes, date_started=date_started, date_ended=date_ended)
            else:
                relationship = RelatedResource.objects.get(pk=relationship_id)
                relationship.relationshiptype = relationship_type_id
                relationship.notes = notes
                relationship.datestarted = date_started
                relationship.dateended = date_ended
                relationship.save()
                se.delete(index='resource_relations', doc_type='all', id=relationship_id)
            se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')

        for relatedentity in original_relations:
            if relatedentity['relationship'].resourcexid not in relationship_ids:
                se.delete(index='resource_relations', doc_type='all', id=relatedentity['relationship'].resourcexid)
                relatedentity['relationship'].delete()

    def load(self, lang):
        data = []
        for relatedentity in self.resource.get_related_resources():
            nodes = relatedentity['related_entity'].flatten()

            data.append({
                'nodes': nodes, 
                'relationship': relatedentity['relationship'], 
                'relationshiptypelabel': get_preflabel_from_valueid(relatedentity['relationship'].relationshiptype, lang)['value'],
                'relatedresourcename':relatedentity['related_entity'].get_primary_name(),
                'relatedresourcetype':relatedentity['related_entity'].entitytypeid,
                'relatedresourceid':relatedentity['related_entity'].entityid,
                'related': True,
            })

        relationship_types = Concept().get_e55_domain('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55')

        try:
            default_relationship_type = relationship_types[0]['id']
            if len(relationship_types) > 6:
                default_relationship_type = relationship_types[6]['id']

            self.data['related-resources'] = {
                'branch_lists': data,
                'domains': {
                    'RELATIONSHIP_TYPES.E32': relationship_types
                },
                'default_relationship_type':  default_relationship_type
            }
            self.data['resource-id'] = self.resource.entityid
        except IndexError:
            pass


class DistrictClassificationForm(ResourceForm):
    baseentity = None

    @staticmethod
    def get_info():
        return {
            'id': 'district_classification',
            'icon': 'fa-adjust',
            'name': _('Classifications'),
            'class': DistrictClassificationForm
        }

    def get_nodes(self, entity, entitytypeid):
        ret = []
        entities = entity.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            ret.append({'nodes': entity.flatten()})

        return ret

    def update_nodes(self, entitytypeid, data):
        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        for value in data[entitytypeid]:
            for newentity in value['nodes']:
                entity = Entity()
                entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                if self.baseentity == None:
                    self.baseentity = entity
                else:
                    self.baseentity.merge(entity)

    def update(self, data, files):

        for value in data['PHASE_TYPE_ASSIGNMENT.E17']:
            for node in value['nodes']:
                if node['entitytypeid'] == 'PHASE_TYPE_ASSIGNMENT.E17' and node['entityid'] != '':
                    #remove the node
                    self.resource.filter(lambda entity: entity.entityid != node['entityid'])

        self.update_nodes('HERITAGE_RESOURCE_GROUP_TYPE.E55', data)
        self.update_nodes('TO_DATE.E49', data)
        self.update_nodes('FROM_DATE.E49', data)
        self.update_nodes('HERITAGE_RESOURCE_GROUP_USE_TYPE.E55', data)
        self.update_nodes('CULTURAL_PERIOD.E55', data)
        self.update_nodes('ANCILLARY_FEATURE_TYPE.E55', data)
        production_entities = self.resource.find_entities_by_type_id('PRODUCTION.E12')

        if len(production_entities) > 0:
            self.resource.merge_at(self.baseentity, 'PRODUCTION.E12')
        else:
            self.resource.merge_at(self.baseentity, self.resource.entitytypeid)
        self.resource.trim()
                   
    def load(self, lang):

        self.data = {
            'data': [],
            'domains': {
                'HERITAGE_RESOURCE_GROUP_TYPE.E55': Concept().get_e55_domain('HERITAGE_RESOURCE_GROUP_TYPE.E55'),
                'HERITAGE_RESOURCE_GROUP_USE_TYPE.E55' : Concept().get_e55_domain('HERITAGE_RESOURCE_GROUP_USE_TYPE.E55'),
                'CULTURAL_PERIOD.E55' : Concept().get_e55_domain('CULTURAL_PERIOD.E55'),
                'ANCILLARY_FEATURE_TYPE.E55' : Concept().get_e55_domain('ANCILLARY_FEATURE_TYPE.E55')
            }
        }

        classification_entities = self.resource.find_entities_by_type_id('PHASE_TYPE_ASSIGNMENT.E17')

        for entity in classification_entities:
            to_date_nodes = datetime_nodes_to_dates(self.get_nodes(entity, 'TO_DATE.E49'))
            from_date_nodes = datetime_nodes_to_dates(self.get_nodes(entity, 'FROM_DATE.E49'))

            self.data['data'].append({
                'HERITAGE_RESOURCE_GROUP_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'HERITAGE_RESOURCE_GROUP_TYPE.E55')
                },
                'HERITAGE_RESOURCE_GROUP_USE_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'HERITAGE_RESOURCE_GROUP_USE_TYPE.E55')
                },
                'CULTURAL_PERIOD.E55': {
                    'branch_lists': self.get_nodes(entity, 'CULTURAL_PERIOD.E55')
                },
                'TO_DATE.E49': {
                    'branch_lists': to_date_nodes
                },
                'FROM_DATE.E49': {
                    'branch_lists': from_date_nodes
                },
                'ANCILLARY_FEATURE_TYPE.E55': {
                    'branch_lists': self.get_nodes(entity, 'ANCILLARY_FEATURE_TYPE.E55')
                },
                'PHASE_TYPE_ASSIGNMENT.E17': {
                    'branch_lists': self.get_nodes(entity, 'PHASE_TYPE_ASSIGNMENT.E17')
                }
            })


class PublicationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'publication',
            'icon': 'fa-flash',
            'name': _('Creation and Publication'),
            'class': PublicationForm
        }

    def update(self, data, files):
        self.update_nodes('RESOURCE_CREATION_EVENT.E65', data)
        self.update_nodes('PUBLICATION_EVENT.E12', data)
        self.update_nodes('RIGHT_TYPE.E55', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['RESOURCE_CREATION_EVENT.E65'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('RESOURCE_CREATION_EVENT.E65')),
                'domains': {
                    'INFORMATION_RESOURCE_TYPE.E55' : Concept().get_e55_domain('INFORMATION_RESOURCE_TYPE.E55')
                }
            }

            self.data['PUBLICATION_EVENT.E12'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('PUBLICATION_EVENT.E12')),
                'domains': {}
            }

            self.data['RIGHT_TYPE.E55'] = {
                'branch_lists': self.get_nodes('RIGHT_TYPE.E55'),
                'domains': {
                    'RIGHT_TYPE.E55' : Concept().get_e55_domain('RIGHT_TYPE.E55')
                }
            }

        return

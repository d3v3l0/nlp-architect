# ******************************************************************************
# Copyright 2017-2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************

import logging
from typing import List

from nlp_architect import LIBRARY_ROOT
from nlp_architect.common.cdc.cluster import Clusters
from nlp_architect.common.cdc.topics import Topics
from nlp_architect.data.cdc_resources.relations.relation_types_enums import RelationType
from nlp_architect.models.cross_doc_coref.cdc_config import EventConfig, EntityConfig
from nlp_architect.models.cross_doc_coref.cdc_resource import CDCResources
from nlp_architect.models.cross_doc_coref.system.cdc_settings import CDCSettings
from nlp_architect.models.cross_doc_coref.system.sieves.sieves import SieveType
from nlp_architect.models.cross_doc_sieves import run_event_coref, run_entity_coref


def run_example():
    event_config = EventConfig()
    event_config.sieves_order = [
        (SieveType.STRICT, RelationType.SAME_HEAD_LEMMA, 0.0),
        (SieveType.VERY_RELAX, RelationType.WIKIPEDIA_DISAMBIGUATION, 0.1),
        (SieveType.VERY_RELAX, RelationType.WORD_EMBEDDING_MATCH, 0.7),
        (SieveType.RELAX, RelationType.SAME_HEAD_LEMMA_RELAX, 0.5),
    ]

    event_config.gold_mentions = Topics(LIBRARY_ROOT
                                        + '/datasets/ecb/ecb_all_event_mentions.json')

    entity_config = EntityConfig()

    entity_config.sieves_order = [
        (SieveType.STRICT, RelationType.SAME_HEAD_LEMMA, 0.0),
        (SieveType.VERY_RELAX, RelationType.WIKIPEDIA_REDIRECT_LINK, 0.1),
        (SieveType.VERY_RELAX, RelationType.WIKIPEDIA_DISAMBIGUATION, 0.1),
        (SieveType.VERY_RELAX, RelationType.WORD_EMBEDDING_MATCH, 0.7),
        (SieveType.VERY_RELAX, RelationType.REFERENT_DICT, 0.5)
    ]

    entity_config.gold_mentions = Topics(LIBRARY_ROOT
                                         + '/datasets/ecb/ecb_all_entity_mentions.json')

    # CDCResources hold default attribute values that might need to be change,
    # (using the defaults values in this example), use to configure attributes
    # such as resources files location, output directory, resources init methods and other.
    # check in class and see if any attributes require change in your set-up
    resource_location = CDCResources()
    resources = CDCSettings(resource_location, event_config, entity_config)

    event_clusters = None
    if event_config.run_evaluation:
        logger.info('Running event coreference resolution')
        event_clusters = run_event_coref(resources)

    entity_clusters = None
    if entity_config.run_evaluation:
        logger.info('Running entity coreference resolution')
        entity_clusters = run_entity_coref(resources)

    print('-=Cross Document Coref Results=-')
    print_results(event_clusters, 'Event')
    print('################################')
    print_results(entity_clusters, 'Entity')


def print_results(clusters: List[Clusters], type: str):
    print('-=' + type + ' Clusters=-')
    for topic_cluster in clusters:
        print('\n\tCluster Topic=' + topic_cluster.topic_id)
        for cluster in topic_cluster.clusters_list:
            cluster_mentions = list()
            for mention in cluster.mentions:
                mentions_dict = dict()
                mentions_dict['id'] = mention.mention_id
                mentions_dict['text'] = mention.tokens_str
                cluster_mentions.append(mentions_dict)

            print('\t\tCluster(' + str(cluster.coref_chain) + ') Mentions='
                  + str(cluster_mentions))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    run_example()

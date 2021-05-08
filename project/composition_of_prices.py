"""
SQL-requests around the topic of (graphical) representations of the composition
of prices.
"""

from graphviz import Graph
from sqlalchemy.orm import aliased
from .models import Angebote, Kaeufe, Produktionsmittel
from .extensions import db


def get_table_of_composition(angebote_id):
    """
    makes a sql request to the db, gives back the composition of price
    (preiszusammensetzung) in table format of the specified Angebot.
    """
    angebote1 = aliased(Angebote)
    angebote2 = aliased(Angebote)
    angebote3 = aliased(Angebote)
    angebote4 = aliased(Angebote)
    angebote5 = aliased(Angebote)

    produktionsmittel1 = aliased(Produktionsmittel)
    produktionsmittel2 = aliased(Produktionsmittel)
    produktionsmittel3 = aliased(Produktionsmittel)
    produktionsmittel4 = aliased(Produktionsmittel)
    produktionsmittel5 = aliased(Produktionsmittel)

    kaeufe2 = aliased(Kaeufe)
    kaeufe3 = aliased(Kaeufe)
    kaeufe4 = aliased(Kaeufe)
    kaeufe5 = aliased(Kaeufe)

    first_level = db.session.query(
        angebote1.id.label("angebot1"), angebote1.name.label("name1"),
        angebote1.p_kosten.label("p1"),
        angebote1.v_kosten.label("v1"), angebote1.preis.label("preis1"),
        produktionsmittel1.prozent_gebraucht.label("proz_gebr2"),
        produktionsmittel1.kauf.label("kauf2"),
        kaeufe2.angebot.label("angebot2"), angebote2.name.label("name2"),
        angebote2.preis.label("preis2"),
        (angebote2.preis*(produktionsmittel1.prozent_gebraucht/100))
        .label("kosten2"),
        produktionsmittel2.prozent_gebraucht.label("proz_gebr3"),
        produktionsmittel2.kauf.label("kauf3"),
        kaeufe3.angebot.label("angebot3"), angebote3.name.label("name3"),
        angebote3.preis.label("preis3"),
        (angebote3.preis*(produktionsmittel2.prozent_gebraucht/100)).
        label("kosten3"),
        produktionsmittel3.prozent_gebraucht.label("proz_gebr4"),
        produktionsmittel3.kauf.label("kauf4"),
        kaeufe4.angebot.label("angebot4"), angebote4.name.label("name4"),
        angebote4.preis.label("preis4"),
        (angebote4.preis*(produktionsmittel3.prozent_gebraucht/100)).
        label("kosten4"),
        produktionsmittel4.prozent_gebraucht.label("proz_gebr5"),
        produktionsmittel4.kauf.label("kauf5"),
        kaeufe5.angebot.label("angebot5"), angebote5.name.label("name5"),
        angebote5.preis.label("preis5"),
        (angebote5.preis*(produktionsmittel4.prozent_gebraucht/100)).
        label("kosten5"),
        produktionsmittel5.prozent_gebraucht.label("proz_gebr6"),
        produktionsmittel5.kauf.label("kauf6"))\
        .select_from(angebote1).filter(angebote1.id == angebote_id).outerjoin(
            produktionsmittel1, angebote1.id == produktionsmittel1.angebot)

    second_level = first_level.outerjoin(
        kaeufe2, produktionsmittel1.kauf == kaeufe2.id).\
        outerjoin(angebote2, kaeufe2.angebot == angebote2.id).\
        outerjoin(produktionsmittel2,
                  angebote2.id == produktionsmittel2.angebot)

    third_level = second_level.outerjoin(
        kaeufe3, produktionsmittel2.kauf == kaeufe3.id).\
        outerjoin(angebote3, kaeufe3.angebot == angebote3.id).\
        outerjoin(
            produktionsmittel3, angebote3.id == produktionsmittel3.angebot)

    fourth_level = third_level.outerjoin(
        kaeufe4, produktionsmittel3.kauf == kaeufe4.id).\
        outerjoin(angebote4, kaeufe4.angebot == angebote4.id).\
        outerjoin(
            produktionsmittel4, angebote4.id == produktionsmittel4.angebot)

    fifth_level = fourth_level.outerjoin(
        kaeufe5, produktionsmittel4.kauf == kaeufe5.id).\
        outerjoin(angebote5, kaeufe5.angebot == angebote5.id).\
        outerjoin(
            produktionsmittel5, angebote5.id == produktionsmittel5.angebot)

    table_of_composition = fifth_level
    return table_of_composition


def get_positions_in_table(base_query):
    """
    takes a 'flask_sqlalchemy.BaseQuery' and creates list of dictionaries that
    stores the info, in which row and column of the database table
    the angebote are positioned
    """
    col1, col2, col3, col4, col5 = [], [], [], [], []
    for row in base_query:
        col1.append(row.name1)
        col2.append(row.name2)
        col3.append(row.name3)
        col4.append(row.name4)
        col5.append(row.name5)
    list_of_cols = [col1, col2, col3, col4, col5]

    cols_dict = []
    for r in range(len(list_of_cols)):
        list1 = []
        for c, i in enumerate(list_of_cols[r]):
            keys_in_list1 = []
            for j in list1:
                if j.keys():
                    keys_in_list1.append(list(j.keys())[0])

            if i in list(keys_in_list1):
                for item in list1:
                    if list(item.keys())[0] == i:
                        item[i].append(c)
            elif i is None:
                pass
            else:
                list1.append({i: [c]})
        cols_dict.append(list1)
    return cols_dict


def create_dots(cols_dict, table_of_composition):
    """
    creates dot nodes and edges based on position of angebote in cols_dict/
    the database table. If angebot x is in the same row and next
    column of angebot y, x is child of y and will be connected with an edge.
    """
    dot = Graph(comment='Graph zur Preiszusammensetzung', format="svg")
    for cnt, col in enumerate(cols_dict):
        if cnt == 0:  # if first column (should be all the same angebot)
            angebot_0 = list(col[0].keys())[0]
            dot.node(
                f"{angebot_0}_{cnt}",
                f"{angebot_0}, "
                f"Preis: {round(table_of_composition[0].preis1, 2)} Std.")
            dot.node(
                f"{angebot_0}_v_{cnt}",
                f"Arbeitskraft: {round(table_of_composition[0].v1, 2)} Std.")
            dot.edge(f"{angebot_0}_{cnt}", f"{angebot_0}_v_{cnt}")
        else:  # the following columns
            for j in col:
                current_angebot = list(j.keys())[0]
                current_position = list(j.values())[0]
                if cnt == 1:
                    current_kosten = round(
                        table_of_composition[current_position[0]].kosten2, 2)
                    dot.node(
                        f"{current_angebot}_{cnt}",
                        f"{current_angebot}, Kosten: {current_kosten} Std.")
                elif cnt in [2, 3, 4]:
                    dot.node(f"{current_angebot}_{cnt}", f"{current_angebot}")

                parent_angebote_list = cols_dict[cnt-1]
                for par in parent_angebote_list:
                    parent_angebot = list(par.keys())[0]
                    parent_positions = list(par.values())[0]
                    for cur_pos in current_position:
                        if cur_pos in parent_positions:
                            # print("MATCH", parent_angebot, current_angebot)
                            # create edge between parent node and current node
                            dot.edge(
                                f"{parent_angebot}_{cnt-1}",
                                f"{current_angebot}_{cnt}")
                            break  # only one match is enough
    return dot

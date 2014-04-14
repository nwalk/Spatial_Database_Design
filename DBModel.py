import psycopg2

def menu():
    print("""
    S - to set up DB
    D - to drop tables
    """)
    x = raw_input("Enter option:")
    if x == 'S':
        setup()
    elif x == 'D':
        takedown()
    else:
        menu()


def setup():
    """Sets up the database"""
    conn = psycopg2.connect("dbname=postgres user=postgres host= password=")
    cur = conn.cursor()
    conn.commit()
    try:
        cur.execute("""CREATE TABLE h_building(
                    id serial PRIMARY KEY,
                    building_name varchar,
                    year integer,
                    location_info varchar,
                    characteristics_summary varchar,
                    characteristics_detail varchar,
                    geom geometry(Polygon,4326));""")
        conn.commit()

        cur.execute("""CREATE TABLE h_property(
                    id serial PRIMARY KEY,
                    property_name varchar,
                    year integer,
                    location_info varchar,
                    characteristics_summary varchar,
                    characteristics_detail varchar,
                    geom geometry(Polygon,4326));""")
        conn.commit()

        cur.execute("""CREATE TABLE h_district(
                    id serial PRIMARY KEY,
                    location_info varchar,
                    characteristics varchar,
                    year integer,
                    geom geometry(Polygon,4326));""")
        conn.commit()

##        cur.execute("""CREATE TABLE h_element(
##                    element_id serial,
##                    h_property_id integer,
##                    element_name varchar,
##                    element_type varchar,
##                    year integer,
##                    characteristics varchar,
##                    geom geometry(Polygon,4326));""")
##        conn.commit()

        cur.execute("""CREATE TABLE h_element(id serial PRIMARY KEY,
                                              type varchar);""")
        conn.commit()

        cur.execute("""CREATE TABLE propelem(id serial,
                    he_id integer REFERENCES h_element(id),
                    hp_id integer REFERENCES h_property(id));""")
        conn.commit()

        cur.execute("""CREATE TABLE bldgelem(
                    id serial, he_id integer REFERENCES h_element(id),
                    hb_id integer REFERENCES h_building(id));""")
        conn.commit()
        
        cur.execute("""ALTER TABLE h_building
                    ADD CONSTRAINT withinprop
                    CHECK (bldg_within_prop(h_building.geom));
                    """)
        conn.commit()

        cur.execute("""ALTER TABLE h_property
                    ADD CONSTRAINT withindist
                    CHECK (prop_within_dist(h_property.geom));
                    """)
        conn.commit()

        cur.execute("""CREATE OR REPLACE FUNCTION bldg_within_prop(g geometry)
                    RETURNS BOOLEAN AS $$
                    BEGIN
                        RETURN ST_Within(g, (SELECT geom FROM h_property));
                    END;
                    $$ LANGUAGE plpgsql;
                    """)
        conn.commit()

        cur.execute("""
                    CREATE OR REPLACE FUNCTION prop_within_dist(g geometry)
                    RETURNS BOOLEAN AS $$
                    BEGIN
                        RETURN ST_Within(g, (SELECT geom FROM h_district));
                    END;
                    $$ LANGUAGE plpgsql;
                    """)
        conn.commit()
    except:
        print("we had problems setting up")
    
    cur.close()
    conn.close()
    print("Complete")
                
def takedown():
    conn = psycopg2.connect("dbname=postgres user=postgres host=localhost password=123456")
    cur = conn.cursor()
    conn.commit()
    try:
        cur.execute("DROP TABLE h_building;")
        cur.execute("DROP TABLE h_property;")
        cur.execute("DROP TABLE h_district;")
        cur.execute("DROP TABLE h_element;")
        cur.execute("DROP TABLE propelem;")
        cur.execute("DROP TABLE bldgelem;")
    except:
        print("we had problems dropping tables")
    
    cur.close()
    conn.close()
    print("Complete")


if __name__ == '__main__':
    menu()

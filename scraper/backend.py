import login
import psycopg2


def is_table_exists(cursor, table_name):
    cursor.execute("SELECT to_regclass('" + table_name + "');")
    return cursor.fetchone()[0] == table_name


def create_table(cursor, table_name):
    cursor.execute( \
        "CREATE TABLE " + table_name + "(" \
            "post_id text NOT NULL," \
            "top_rank smallint NOT NULL," \
            "time_top_rank_achieved timestamptz NOT NULL," \
            "category text NOT NULL," \
            "title text NOT NULL," \
            "link text NOT NULL," \
            "author_name text NOT NULL," \
            "updated timestamptz NOT NULL," \
            "content text NOT NULL" \
        ");" \
    )


def get_record(cursor, table_name, post_id):
    cursor.execute( \
        "SELECT * " \
        "FROM " + table_name + " " \
        "WHERE post_id = '" + post_id + "';" \
    )
    return cursor.fetchone()


def get_results(cursor, table_name, threshold_rank):
    cursor.execute( \
        "SELECT * " \
        "FROM " + table_name + " " \
        "WHERE top_rank <= " + str(threshold_rank) + " " \
        "ORDER BY time_top_rank_achieved DESC;"
    )
    return cursor.fetchall()


def get_subreddits(cursor, table_name):
    cursor.execute( \
        "SELECT DISTINCT category " \
        "FROM " + table_name + ";"
    )
    return cursor.fetchall()


def modify_record(cursor, table_name, post_id, rank, category, title, link, author_name, updated, content):
    # add record
    # commit
    # call get_record
    # if empty
        # add record
        # commit
    #else #not empty
        # check the rank of the existing record
        # if existing rank > record rank
            # update record
            # commit
    lookup = get_record(cursor, table_name, post_id)
    if lookup == None:
        cursor.execute("SELECT NOW();")
        time_top_rank_achieved = str(cursor.fetchone()[0])
        cursor.execute( \
            "INSERT INTO " + table_name + " " \
            "(post_id, top_rank, time_top_rank_achieved, category, title, link, author_name, updated, content) " \
            "VALUES ('" + post_id + "'," + str(rank) + ",'" + time_top_rank_achieved + "','" + category + "','" + title + "','" + link + "','" + author_name + "','" + updated + "','" + content + "');" \
        )
    elif lookup[1] > rank: # if existing_in_table < current_rank_to_maybe_put_in_table
	cursor.execute("SELECT NOW();")
        time_top_rank_achieved = str(cursor.fetchone()[0])
        cursor.execute( \
	cursor.execute( \
            "UPDATE " + table_name + " " \
            "SET top_rank = " + str(rank) + ", time_top_rank_achieved = '" + time_top_rank_achieved + "' " \
            "WHERE post_id = '" + post_id + "';"
        )


def test_case(cursor, table_name):
    print("setup 0")
    modify_record(cursor, table_name, "tifu_qwe", 1, "tifu", "tifu somehow", "google.com", "me", '2019-06-14 19:10:25-07', 'my content')
    print("setup 1")
    modify_record(cursor, table_name, "jokes_abc", 5, "jokes", "6 afraid of 7", "youtube.com" "you", '2016-06-22 19:10:25-07', 'your content')
    print("test case 1")
    print(get_record(cursor, table_name, "tifu_qwe"))
    print("test case 2")
    print(get_record(cursor, table_name, "jokes_abc"))
    print("test case 3")
    print(get_record(cursor, table_name, "should not exist"))
    print("setup 2")
    modify_record(cursor, table_name, "tifu_qwe", 3, "tifu", "tifu somehow", "facebook.com", "me", '2019-06-14 19:10:25-07', 'her content')
    record_to_check = get_record(cursor, table_name, "tifu_qwe")
    if record_to_check[1] == 1:
        print("test case 4 passed")
    else:
        print("test case 4 failed")
    print("setup 3")
    modify_record(cursor, table_name, "jokes_abc", 3, "jokes", "6 afraid of 7", "amazon.com", "you", '2016-06-22 19:10:25-07', 'his content')
    record_to_check = get_record(cursor, table_name, "jokes_abc")
    if record_to_check[1] == 3:
        print("test case 5 passed")
    else:
        print("test case 5 failed")
    print("test case 6: should print nothing")
    print(get_results(cursor, table_name, 0))
    print("test case 7: should print 1 thing")
    print(get_results(cursor, table_name, 2))
    print("test case 8: should print 2 things")
    print(get_results(cursor, table_name, 3))


def get_connection():
    return psycopg2.connect(user     = login.connection_details["user"],
                            password = login.connection_details["password"],
                            host     = login.connection_details["host"],
                            port     = login.connection_details["port"],
                            database = login.connection_details["database"])
   

def close_connection(connection):
    if (connection):
        connection.cursor().close()
        connection.close()
        print("PostgreSQL connection is closed")
    return; 

def main():
    try:
        connection = get_connection() 
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(),"\n")
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        test_case(cursor, "test_table")
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        close_connection(connection)


if __name__ == '__main__':
    main()


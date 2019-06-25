import psycopg2

TABLE_NAME = "top_posts"

def is_table_exists(cursor, table_name):
    cursor.execute("SELECT to_regclass('" + table_name + "');")
    return cursor.fetchone()[0] == table_name

def create_table(cursor):
    cursor.execute( \
        "CREATE TABLE " + TABLE_NAME + "(" \
            "subreddit_post_hash text NOT NULL," \
            "top_rank smallint NOT NULL," \
            "time_top_rank_achieved timestamptz NOT NULL," \
            "subreddit text NOT NULL," \
            "title text NOT NULL," \
            "username text NOT NULL," \
            "creation_date timestamptz NOT NULL" \
        ");" \
    )

def get_record(cursor, subreddit_post_hash):
    cursor.execute( \
        "SELECT * " \
        "FROM " + TABLE_NAME + " " \
        "WHERE subreddit_post_hash = '" + subreddit_post_hash + "';" \
    )
    return cursor.fetchone()

def get_results(cursor, threshold_rank):
    cursor.execute( \
        "SELECT * " \
        "FROM " + TABLE_NAME + " " \
        "WHERE top_rank <= " + str(threshold_rank) + " " \
        "ORDER BY time_top_rank_achieved DESC;"
    )
    return cursor.fetchall()

def modify_record(cursor, subreddit_post_hash, rank, subreddit, title, username, creation_date):
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
    lookup = get_record(cursor, subreddit_post_hash)
    if lookup == None:
        cursor.execute("SELECT NOW();")
        time_top_rank_achieved = str(cursor.fetchone()[0])
        cursor.execute( \
            "INSERT INTO " + TABLE_NAME + " " \
            "(subreddit_post_hash, top_rank, time_top_rank_achieved, subreddit, title, username, creation_date) " \
            "VALUES ('" + subreddit_post_hash + "'," + str(rank) + ",'" + time_top_rank_achieved + "','" + subreddit + "','" + title + "','" + username + "','" + creation_date + "');" \
        )
    else:
        if lookup[1] > rank: # if existing_in_table < current_rank_to_maybe_put_in_table
            cursor.execute( \
                "UPDATE " + TABLE_NAME + " " \
                "SET top_rank = " + str(rank) + " " \
                "WHERE subreddit_post_hash = '" + subreddit_post_hash + "';"
            )

def test_case(cursor):
    print("setup 0")
    modify_record(cursor, "tifu_qwe", 1, "tifu", "tifu somehow", "me", '2019-06-14 19:10:25-07')
    print("setup 1")
    modify_record(cursor, "jokes_abc", 5, "jokes", "6 afraid of 7", "you", '2016-06-22 19:10:25-07')
    print("test case 1")
    print(get_record(cursor, "tifu_qwe"))
    print("test case 2")
    print(get_record(cursor, "jokes_abc"))
    print("test case 3")
    print(get_record(cursor, "should not exist"))
    print("setup 2")
    modify_record(cursor, "tifu_qwe", 3, "tifu", "tifu somehow", "me", '2019-06-14 19:10:25-07')
    record_to_check = get_record(cursor, "tifu_qwe")
    if record_to_check[1] == 1:
        print("test case 4 passed")
    else:
        print("test case 4 failed")
    print("setup 3")
    modify_record(cursor, "jokes_abc", 3, "jokes", "6 afraid of 7", "you", '2016-06-22 19:10:25-07')
    record_to_check = get_record(cursor, "jokes_abc")
    if record_to_check[1] == 3:
        print("test case 5 passed")
    else:
        print("test case 5 failed")
    print("test case 6: should print nothing")
    print(get_results(cursor, 0))
    print("test case 7: should print 1 thing")
    print(get_results(cursor, 2))
    print("test case 8: should print 2 things")
    print(get_results(cursor, 3))

try:
    connection = psycopg2.connect(user = "allen",
                                  password = "123123qwer",
                                  host = "104.155.165.207",
                                  port = "5432",
                                  database = "reddit_db")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(),"\n")
    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    test_case(cursor)
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

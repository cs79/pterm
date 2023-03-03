import sqlite3
import cmd
from pgp_ops import *

def db_setup():
    """Create the database and table if it doesn't exist."""
    conn = sqlite3.connect('pterm.db')
    c = conn.cursor()
    # create a core database table to contain identifying information about this terminal
    # this table (for now) will only contain one record, the record for this node
    # TODO: consider what identifying information is missing - networking info ? or in a separate table ? etc.
    c.execute('''CREATE TABLE IF NOT EXISTS core
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_name TEXT NOT NULL,
                    node_pubkey TEXT NULLABLE,
                    node_privkey_path TEXT NULLABLE,
                    prompt TEXT NULLABLE)''')
    # create a peers database table to contain contact information about other nodes
    # these nodes will be able to exchange messages peer-to-peer with each other / other pterms
    # TODO: probably need something like hash of a public key to identify a node...
    c.execute('''CREATE TABLE IF NOT EXISTS peers
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_name TEXT NOT NULL,
                    node_pubkey TEXT NOT NULL,
                    node_ip TEXT NOT NULL)''')
    # create a messages database table to contain messages sent between nodes
    # any pterm can act as a relay for messages between nodes; policy will determine how long to keep messages
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dest_node_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp_last_forwarding_attempt TEXT NOT NULL,
                    delivery_success BOOLEAN NOT NULL)''')
    # TODO: add other tables as needed
    
    conn.commit()
    conn.close()

class Pterm(cmd.Cmd):
    """Pterm is a command line interface for a user pterminal."""

    # check if the database exists, if not create it
    db_setup()
    # check if the core table contains a record for this node, if not create it
    conn = sqlite3.connect('pterm.db')
    c = conn.cursor()
    c.execute('SELECT * FROM core')
    if c.fetchone() is None:
        print('No core record found, creating one...')
        # prompt the user for the information needed to create a core record
        user_node_name = input('Enter a name for this node: ')
        # construct the text of the query, inserting user_node_name as the value for node_name
        qry = 'INSERT INTO core (node_name, node_pubkey, node_privkey_path, prompt) VALUES ("' + user_node_name + '", "test_node_pubkey", "test_node_privkey_path", "pterm>")'
        c.execute(qry)
        conn.commit()
    
    # check if the first record in the core table contains a prompt, if not, use a default
    c.execute('SELECT * FROM core')
    prompt = 'pterm> '
    record = c.fetchone()
    if record[4] is not None:
        prompt = record[4] + ' '
    
    #--------------------#
    # Developer commands #
    #--------------------#

    # command to drop and rebuild the core table (i.e., reset this node's information)
    def do_drop_core(self, args):
        """Drop and rebuild the core table."""
        conn = sqlite3.connect('pterm.db')
        c = conn.cursor()
        c.execute('DROP TABLE core')
        c.execute('''CREATE TABLE core
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_name TEXT NOT NULL,
                    node_pubkey TEXT NULLABLE,
                    node_privkey_path TEXT NULLABLE,
                    prompt TEXT NULLABLE)''')
        conn.commit()
        conn.close()
    
    def do_list_core(self, args):
        """List all entries from the core table."""
        conn = sqlite3.connect('pterm.db')
        c = conn.cursor()
        c.execute('SELECT * FROM core')
        print(c.fetchall())

    #-------------------#
    # Terminal commands #
    #-------------------#

    # command to view own node information
    def do_whoami(self, args):
        """View own node information."""
        conn = sqlite3.connect('pterm.db')
        c = conn.cursor()
        c.execute('SELECT * FROM core')
        record = c.fetchone()
        if record is None:
            print('No core record found.')
            return
        print('Node name: ' + record[1])
        print('Node public key: ' + record[2])
        print('Node private key path: ' + record[3])
        print('Prompt: ' + record[4])

    # command to update the prompt
    def do_set_prompt(self, new_prompt):
        """Set the prompt for this pterm."""
        # update the core table record for this node with the new_prompt as the prompt value
        conn = sqlite3.connect('pterm.db')
        c = conn.cursor()
        qry = 'UPDATE core SET prompt = "' + new_prompt + '" WHERE id = 1'
        c.execute(qry)
        conn.commit()
        # update the prompt
        self.prompt = new_prompt + ' '

    # command to generate new keys
    # TODO: prompt for needed User ID info (if we want to use PGP here), add it to keypair, and persist properly -- this is placeholder for now
    def do_gen_keys(self, args):
        """Generate new keys."""
        # generate new keys
        keypair = gen_keypair()
        # update the core table record for this node with the new keys
        conn = sqlite3.connect('pterm.db')
        c = conn.cursor()
        qry = 'UPDATE core SET node_pubkey = "' + keypair.fingerprint + '", node_privkey_path = "" WHERE id = 1'
        c.execute(qry)
        conn.commit()
        conn.close()

    def do_exit(self, args):
        """Exit the program."""
        print('Exiting...')
        return True

    def do_EOF(self, args):
        """Exit the program."""
        print('Exiting...')
        return True

def main():
    Pterm().cmdloop()

if __name__ == '__main__':
    main()

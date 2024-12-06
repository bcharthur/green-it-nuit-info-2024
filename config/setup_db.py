# config/setup_db.py
import pyodbc
import sys

# Paramètres de connexion
SERVER = 'localhost'  # Nom du serveur SQL
USER = 'sa'
PASSWORD = '123456789'
DRIVER = 'ODBC Driver 17 for SQL Server'
DB_NAME = 'db_green'


def database_exists(cursor, db_name):
    cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (db_name,))
    row = cursor.fetchone()
    return row is not None


def table_exists(cursor, table_name):
    cursor.execute("SELECT OBJECT_ID(?)", (table_name,))
    row = cursor.fetchone()
    return row is not None and row[0] is not None


def constraint_exists(cursor, table_name, constraint_name):
    cursor.execute("""
        SELECT * FROM sys.foreign_keys 
        WHERE parent_object_id = OBJECT_ID(?) AND name = ?
    """, (table_name, constraint_name))
    return cursor.fetchone() is not None


def main():
    try:
        # Connexion initiale au serveur (à la base master) avec autocommit=True
        conn_server = pyodbc.connect(
            f'DRIVER={{{DRIVER}}};SERVER={SERVER};UID={USER};PWD={PASSWORD};Trusted_Connection=no;DATABASE=master;',
            autocommit=True  # Important pour CREATE DATABASE
        )
        cursor_server = conn_server.cursor()

        # Vérifier si la base db_green existe, sinon la créer
        if not database_exists(cursor_server, DB_NAME):
            print(f"La base {DB_NAME} n'existe pas. Création en cours...")
            cursor_server.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Base {DB_NAME} créée avec succès.")
        else:
            print(f"La base {DB_NAME} existe déjà.")

        # Connexion à la base db_green (autocommit=False par défaut)
        conn_db = pyodbc.connect(
            f'DRIVER={{{DRIVER}}};SERVER={SERVER};UID={USER};PWD={PASSWORD};Trusted_Connection=no;DATABASE={DB_NAME};'
        )
        cursor_db = conn_db.cursor()

        # Création des tables si elles n'existent pas

        # Table images
        if not table_exists(cursor_db, 'images'):
            print("Table 'images' inexistante. Création en cours...")
            cursor_db.execute("""
                CREATE TABLE images (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    hash VARCHAR(64) UNIQUE NOT NULL,
                    original_image VARBINARY(MAX),
                    compressed_image VARBINARY(MAX)
                )
            """)
            conn_db.commit()
            print("Table 'images' créée.")

        # Table item
        if not table_exists(cursor_db, 'item'):
            print("Table 'item' inexistante. Création en cours...")
            cursor_db.execute("""
                CREATE TABLE item (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    label VARCHAR(255) NOT NULL,
                    image_id INT NULL
                )
            """)
            conn_db.commit()
            print("Table 'item' créée.")

        # Ajouter ou mettre à jour la contrainte FK_item_images avec ON DELETE SET NULL
        constraint_name = "FK_item_images"
        if not constraint_exists(cursor_db, 'item', constraint_name):
            print(f"Ajout de la contrainte {constraint_name} avec ON DELETE SET NULL...")
            cursor_db.execute("""
                ALTER TABLE item
                ADD CONSTRAINT FK_item_images
                FOREIGN KEY (image_id) REFERENCES images(id)
                ON DELETE SET NULL
            """)
            conn_db.commit()
            print(f"Contrainte {constraint_name} ajoutée.")
        else:
            print(f"Contrainte {constraint_name} existe déjà.")

        # Table image_stats
        if not table_exists(cursor_db, 'image_stats'):
            print("Table 'image_stats' inexistante. Création en cours...")
            cursor_db.execute("""
                CREATE TABLE image_stats (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    item_id INT NOT NULL,
                    original_size INT NOT NULL,
                    compressed_size INT NOT NULL,
                    co2_economise FLOAT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
                )
            """)
            conn_db.commit()
            print("Table 'image_stats' créée avec ON DELETE CASCADE.")

        # Table api_logs
        if not table_exists(cursor_db, 'api_logs'):
            print("Table 'api_logs' inexistante. Création en cours...")
            cursor_db.execute("""
                CREATE TABLE api_logs (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    userVar VARCHAR(255),
                    methodVar VARCHAR(10),
                    timestampVar DATETIME DEFAULT GETDATE(),
                    endpoint VARCHAR(255),
                    json_response VARCHAR(MAX)
                )
            """)
            conn_db.commit()
            print("Table 'api_logs' créée.")
        else:
            print("Table 'api_logs' existe déjà.")

        print("Vérification terminée. Toutes les tables nécessaires existent.")

    except Exception as e:
        print(f"Erreur lors de la configuration de la base de données : {e}")
        sys.exit(1)

    finally:
        try:
            conn_db.close()
        except:
            pass
        try:
            conn_server.close()
        except:
            pass


if __name__ == '__main__':
    main()

import xmlrpc.client
import logging
import os


logging.basicConfig(level=logging.DEBUG)


ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "Admin")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "arjukushwaha6689@gmail.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

class OdooClient:
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD

        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                logging.error("Authentication failed! Check credentials.")
                raise Exception("Authentication failed")
            
            self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
            logging.info(f"Authenticated with UID: {self.uid}")
        
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            raise

    def update_user_permissions(self):
        """ Assign 'Administration / Settings' group to the current user """
        user_id = self.uid
        try:
            group_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.groups', 'search', [[('name', '=', 'Administration / Settings')]]
            )
            if group_id:
                self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.users', 'write', [[user_id], {'groups_id': [(6, 0, group_id)]}]
                )
                logging.info("User permissions updated successfully.")
            else:
                logging.error("Group not found.")
        except xmlrpc.client.Fault as e:
            logging.error(f"Odoo XML-RPC error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error updating permissions: {e}")

    def create_lead(self, name, email):
        """ Create a new CRM lead """
        logging.debug(f"Creating lead: {name}, {email}")
        try:
            lead_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'crm.lead', 'create',
                [{'name': name, 'email_from': email}]  
            )
            logging.info(f"Lead created with ID: {lead_id}")
            return lead_id
        except xmlrpc.client.Fault as e:
            logging.error(f"Odoo XML-RPC error: {e}")
        except Exception as e:
            logging.error(f"Error creating lead: {e}")
        return None

    def create_customer(self, name, email, phone):
        """ Create a new customer (res.partner) """
        logging.debug(f"Creating customer: {name}, {email}, {phone}")
        try:
            customer_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'create',
                [{'name': name, 'email': email, 'phone': phone}]
            )
            logging.info(f"Customer created with ID: {customer_id}")
            return customer_id
        except xmlrpc.client.Fault as e:
            logging.error(f"Odoo XML-RPC error: {e}")
        except Exception as e:
            logging.error(f"Error creating customer: {e}")
        return None
    def delete_lead(self, lead_id):
        logging.debug(f"Deleting lead with ID: {lead_id}")
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'crm.lead', 'unlink', [[lead_id]]
            )
            logging.info(f"Lead with ID {lead_id} deleted successfully.")
            return True
        except xmlrpc.client.Fault as e:
            logging.error(f"Odoo XML-RPC error: {e}")
        except Exception as e:
            logging.error(f"Error deleting lead: {e}")
        return False
    
    def delete_customer(self, customer_id):
    
        logging.debug(f"Deleting customer with ID: {customer_id}")
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'unlink', [[customer_id]]
            )
            logging.info(f"Customer with ID {customer_id} deleted successfully.")
            return True
        except xmlrpc.client.Fault as e:
            logging.error(f"Odoo XML-RPC error: {e}")
        except Exception as e:
            logging.error(f"Error deleting customer: {e}")
        return False
    def update_customer(self, customer_id, name, email, phone):
        logging.debug(f"Updating customer in Odoo: ID={customer_id}, Name={name}, Email={email}, Phone={phone}")
         
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'write', [[customer_id], {'name': name, 'email': email, 'phone': phone}]
            )
            logging.info(f"Customer with ID {customer_id} updated successfully in Odoo.")
        except Exception as e:
            logging.error(f"Error updating customer in Odoo: {e}")

    def update_lead(self, lead_id, name, email):
        logging.debug(f"Updating lead in Odoo: ID={lead_id}, Name={name}, Email={email}")
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'crm.lead', 'write', [[lead_id], {'name': name, 'email_from': email}]
            )
            logging.info(f"Lead with ID {lead_id} updated successfully in Odoo.")
        except Exception as e:
            logging.error(f"Error updating lead in Odoo: {e}")

if __name__ == "__main__":
    try:
        client = OdooClient()
        client.update_user_permissions()
        
        # Add a lead
        lead_id = client.create_lead("John Doe", "john.doe@example.com")
        if lead_id:
            logging.info(f"Lead successfully created with ID: {lead_id}")
        else:
            logging.error("Failed to create lead")

        # Add a customer
        customer_id = client.create_customer("Jane Doe", "jane.doe@example.com", "1234567890")
        if customer_id:
            logging.info(f"Customer successfully created with ID: {customer_id}")
        else:
            logging.error("Failed to create customer")
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

"""Integration test against SAP"""
import unittest
import os
from itk_dev_shared_components.sap import sap_login, multi_session
from afskrivining_af_foraeldede_sagsomkostninger.sap_process import delete_cost

class RunProcess(unittest.TestCase):
    """This is an intergration test"""
    def test_afskrivning(self):
        """Test afskrivning process on hard coded values.
        Setup: enter sap credentials in env vars as 'username;password' """

        credentials = os.getenv('SAP login').split(';')
        sap_login.login_using_cli(credentials[0], credentials[1])
        session = multi_session.get_all_sap_sessions()[0]

        fp = '50015577'
        aftale = '1882120'
        bilag = "222000515037"
        delete_cost(session=session, fp=fp, aftale=aftale, bilag=bilag, dry_run=True)



if __name__ == '__main__':
    unittest.main()

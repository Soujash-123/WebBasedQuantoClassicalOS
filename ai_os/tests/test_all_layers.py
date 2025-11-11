"""
Comprehensive Test Suite for AI OS v1.0
Tests all layers and their integration.
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestMemoryLayer(unittest.TestCase):
    """Test Memory Layer"""
    
    def setUp(self):
        from ai_os.memory_layer import MemoryLayer
        self.memory = MemoryLayer(total_memory_mb=128, page_size_kb=4)
        self.memory.initialize()
    
    def tearDown(self):
        self.memory.shutdown()
    
    def test_memory_allocation(self):
        """Test memory allocation"""
        result = self.memory.allocate(process_id=1, size_mb=16)
        self.assertTrue(result, "Memory allocation should succeed")
    
    def test_memory_stats(self):
        """Test memory statistics"""
        stats = self.memory.get_stats()
        self.assertIn('total_memory_mb', stats)
        self.assertEqual(stats['total_memory_mb'], 128)
    
    def test_memory_free(self):
        """Test memory deallocation"""
        self.memory.allocate(process_id=2, size_mb=16)
        freed = self.memory.free(process_id=2)
        self.assertGreater(freed, 0, "Should free some pages")
    
    def test_memstat_command(self):
        """Test memstat command"""
        result = self.memory.cmd_memstat()
        self.assertIn('MEMORY STATISTICS', result)


class TestNetworkLayer(unittest.TestCase):
    """Test Network Layer"""
    
    def setUp(self):
        from ai_os.network_layer import NetworkLayer
        self.network = NetworkLayer()
        self.network.initialize()
    
    def tearDown(self):
        self.network.shutdown()
    
    def test_get_hostname(self):
        """Test hostname retrieval"""
        hostname = self.network.get_hostname()
        self.assertIsNotNone(hostname)
        self.assertIsInstance(hostname, str)
    
    def test_get_local_ip(self):
        """Test local IP retrieval"""
        ip = self.network.get_local_ip()
        self.assertIsNotNone(ip)
        self.assertIsInstance(ip, str)
    
    def test_netinfo_command(self):
        """Test netinfo command"""
        result = self.network.cmd_netinfo()
        self.assertIn('NETWORK INFORMATION', result)
    
    def test_ifconfig_command(self):
        """Test ifconfig command"""
        result = self.network.cmd_ifconfig()
        self.assertIn('NETWORK INTERFACES', result)


class TestSecurityLayer(unittest.TestCase):
    """Test Security Layer"""
    
    def setUp(self):
        from ai_os.security_layer import SecurityLayer
        import tempfile
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_db.close()
        self.security = SecurityLayer(user_db_path=self.temp_db.name)
        self.security.initialize()
    
    def tearDown(self):
        self.security.shutdown()
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_create_user(self):
        """Test user creation"""
        result = self.security.auth.create_user('testuser', 'testpass')
        self.assertTrue(result, "User creation should succeed")
    
    def test_authentication(self):
        """Test user authentication"""
        self.security.auth.create_user('authtest', 'password123')
        token = self.security.auth.authenticate('authtest', 'password123')
        self.assertIsNotNone(token, "Authentication should succeed")
    
    def test_encryption(self):
        """Test encryption/decryption"""
        data = "Hello, World!"
        encrypted = self.security.encryption.encrypt_data(data)
        self.assertIsInstance(encrypted, bytes)
        
        decrypted = self.security.encryption.decrypt_data(encrypted)
        self.assertEqual(decrypted.decode(), data)
    
    def test_hashing(self):
        """Test hashing"""
        data = "test data"
        hash_result = self.security.hashing.hash_sha256(data)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "secure_password"
        hash_val, salt = self.security.hashing.hash_password(password)
        
        # Verify correct password
        result = self.security.hashing.verify_password(password, hash_val, salt)
        self.assertTrue(result)
        
        # Verify incorrect password
        result = self.security.hashing.verify_password("wrong", hash_val, salt)
        self.assertFalse(result)


class TestDiagnosticsLayer(unittest.TestCase):
    """Test Diagnostics Layer"""
    
    def setUp(self):
        from ai_os.diagnostics import DiagnosticsLayer
        self.diagnostics = DiagnosticsLayer()
        self.diagnostics.initialize()
    
    def tearDown(self):
        self.diagnostics.shutdown()
    
    def test_system_check(self):
        """Test system diagnostics"""
        summary = self.diagnostics.system_check.run_all_checks()
        self.assertIn('overall_status', summary)
        self.assertIn('results', summary)
    
    def test_resource_monitor(self):
        """Test resource monitoring"""
        stats = self.diagnostics.resource_monitor.get_current_stats()
        self.assertIn('timestamp', stats)
        self.assertIn('cpu_percent', stats)
    
    def test_syscheck_command(self):
        """Test syscheck command"""
        result = self.diagnostics.cmd_syscheck()
        self.assertIn('SYSTEM DIAGNOSTIC REPORT', result)


class TestIntegration(unittest.TestCase):
    """Test layer integration"""
    
    def setUp(self):
        from ai_os.os_master import AIOSMaster
        self.os_master = AIOSMaster()
        self.os_master.initialize()
    
    def tearDown(self):
        self.os_master.shutdown()
    
    def test_all_layers_initialized(self):
        """Test that all layers are initialized"""
        expected_layers = ['memory', 'network', 'security', 'diagnostics']
        for layer in expected_layers:
            self.assertIn(layer, self.os_master.layers, f"{layer} should be initialized")
    
    def test_command_registry(self):
        """Test command registration"""
        commands = self.os_master.get_all_commands()
        self.assertGreater(len(commands), 0, "Should have registered commands")
        
        # Check for key commands
        expected_commands = ['memstat', 'ping', 'login', 'syscheck']
        for cmd in expected_commands:
            self.assertIn(cmd, commands, f"{cmd} should be registered")
    
    def test_command_execution(self):
        """Test command execution"""
        # Test memstat
        result = self.os_master.execute_command('memstat')
        self.assertIn('MEMORY', result)
        
        # Test netinfo
        result = self.os_master.execute_command('netinfo')
        self.assertIn('NETWORK', result)
    
    def test_memory_network_integration(self):
        """Test memory and network layer working together"""
        # Allocate memory
        memory_layer = self.os_master.get_layer('memory')
        memory_layer.allocate(1, 32)
        
        # Check network is still functional
        network_layer = self.os_master.get_layer('network')
        hostname = network_layer.get_hostname()
        self.assertIsNotNone(hostname)


def run_tests():
    """Run all tests"""
    print("="*70)
    print("AI OS v1.0 - Comprehensive Test Suite")
    print("="*70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagnosticsLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())

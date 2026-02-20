#!/usr/bin/env python3
"""
Test script to help configure Oracle Autonomous Database connection without wallet
"""

import oracledb
import os
from decouple import config

def test_connection(dsn, user, password):
    """Test a specific connection string"""
    try:
        print(f"Testing connection to: {dsn}")
        connection = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
            config_dir=None,
            wallet_location=None,
            wallet_password=None
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 'Connected successfully!' FROM dual")
        result = cursor.fetchone()
        print(f"✅ {result[0]}")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    user = config('DB_USER', default='admin')
    password = config('DB_PASSWORD', default='AIhackathon2026')
    service_name = 'uexulb26uojc2pyx_high'  # Your service name

    print("🔍 Testing Oracle Autonomous Database connections without wallet...")
    print(f"User: {user}")
    print(f"Service: {service_name}")
    print()

    # Common Oracle Cloud regions to try
    regions = [
        'us-ashburn-1',
        'us-phoenix-1',
        'eu-frankfurt-1',
        'uk-london-1',
        'ca-toronto-1',
        'ap-tokyo-1',
        'ap-sydney-1'
    ]

    successful_connections = []

    for region in regions:
        host = f'adb.{region}.oraclecloud.com'
        dsn = f'{host}:1521/{service_name}'

        if test_connection(dsn, user, password):
            successful_connections.append(dsn)

    print()
    if successful_connections:
        print("✅ Successful connections found:")
        for dsn in successful_connections:
            print(f"   {dsn}")

        print()
        print("📝 Update your .env file with one of these DSN values:")
        print(f"   DB_DSN={successful_connections[0]}")
    else:
        print("❌ No successful connections found.")
        print()
        print("💡 Troubleshooting tips:")
        print("   1. Check your Oracle Cloud Console for the correct host")
        print("   2. Verify your username and password")
        print("   3. Make sure your IP is allowlisted in Oracle Cloud")
        print("   4. Try using wallet authentication instead")
        print()
        print("🔍 To find your host in Oracle Cloud Console:")
        print("   1. Go to Autonomous Database details")
        print("   2. Click 'Database connection'")
        print("   3. Look for the 'Connection string' section")
        print("   4. Use the host from the EZ Connect format")

if __name__ == "__main__":
    main()
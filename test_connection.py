from database import get_supabase_client

# Test Supabase connection
supabase = get_supabase_client()

try:
    # Try to query the transactions table
    response = supabase.table("transactions").select("*").limit(1).execute()
    print("✓ Supabase connection successful!")
    print(f"✓ Table 'transactions' exists")
    print(f"Response: {response}")
except Exception as e:
    print(f"✗ Error connecting to Supabase: {e}")

import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getAccountsApi, getTransactionsApi } from '@/api/client';
import { Theme } from '@/constants/PayFastTheme';
import { Wallet, Activity, ArrowUpRight, ArrowDownLeft } from 'lucide-react-native';

export default function DashboardScreen() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [accs, txData] = await Promise.all([
        getAccountsApi(),
        getTransactionsApi()
      ]);
      setAccounts(accs || []);
      setTransactions(txData?.items || []);
    } catch (e) {
      console.log('Error loading data', e);
    }
  };

  useEffect(() => {
    loadData().finally(() => setLoading(false));
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadData().finally(() => setRefreshing(false));
  }, []);

  const totalBalance = accounts.reduce((acc, curr) => acc + (curr.balance_paise || 0), 0) / 100;

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={Theme.colors.accentPrimary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Theme.colors.accentPrimary} />}
      >
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Overview</Text>
          <Text style={styles.headerSubtitle}>Your financial summary</Text>
        </View>

        <View style={styles.balanceCard}>
          <View style={styles.cardHeader}>
            <View style={styles.iconBox}>
              <Wallet size={20} color={Theme.colors.accentPrimary} />
            </View>
            <Text style={styles.cardLabel}>Total Balance</Text>
          </View>
          <Text style={styles.balanceText}>${totalBalance.toFixed(2)}</Text>
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Accounts</Text>
        </View>
        <View style={styles.accountsList}>
          {accounts.length === 0 ? (
            <Text style={styles.emptyText}>No accounts found.</Text>
          ) : (
            accounts.map(acc => (
              <View key={acc.id} style={styles.accountItem}>
                <View>
                  <Text style={styles.accountType}>{acc.account_type}</Text>
                  <Text style={styles.accountNumber}>{acc.account_number}</Text>
                </View>
                <Text style={styles.accountBalance}>${(acc.balance_paise / 100).toFixed(2)}</Text>
              </View>
            ))
          )}
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
        </View>
        <View style={styles.transactionsList}>
          {transactions.length === 0 ? (
            <Text style={styles.emptyText}>No recent transactions</Text>
          ) : (
            transactions.map((tx, idx) => {
              const isDebit = tx.transaction_type === 'transfer_out' || tx.transaction_type === 'withdrawal';
              const amount = (tx.amount_paise / 100).toFixed(2);
              const isLast = idx === transactions.length - 1;

              return (
                <View key={tx.id} style={[styles.transactionItem, !isLast && styles.transactionItemBorder]}>
                  <View style={styles.txLeft}>
                    <View style={[styles.txIconBox, { backgroundColor: isDebit ? 'rgba(255, 51, 102, 0.1)' : 'rgba(0, 255, 187, 0.1)' }]}>
                      {isDebit ? 
                        <ArrowUpRight size={18} color={Theme.colors.accentDanger} /> : 
                        <ArrowDownLeft size={18} color={Theme.colors.accentSecondary} />
                      }
                    </View>
                    <View>
                      <Text style={styles.txType}>{tx.transaction_type}</Text>
                      <Text style={styles.txRef}>{tx.reference_number || 'REF'}</Text>
                    </View>
                  </View>
                  <Text style={[styles.txAmount, { color: isDebit ? Theme.colors.textPrimary : Theme.colors.accentSecondary }]}>
                    {isDebit ? '-' : '+'}${amount}
                  </Text>
                </View>
              );
            })
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Theme.colors.background,
  },
  scrollContent: {
    padding: Theme.spacing.l,
    paddingBottom: Theme.spacing.xxl,
  },
  header: {
    marginBottom: Theme.spacing.l,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Theme.colors.textPrimary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: Theme.colors.textSecondary,
    marginTop: Theme.spacing.s,
  },
  balanceCard: {
    backgroundColor: Theme.colors.backgroundGlass,
    padding: Theme.spacing.l,
    borderRadius: Theme.radii.l,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    marginBottom: Theme.spacing.l,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Theme.spacing.m,
    marginBottom: Theme.spacing.m,
  },
  iconBox: {
    padding: 8,
    borderRadius: Theme.radii.s,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  cardLabel: {
    color: Theme.colors.textSecondary,
    fontSize: 16,
  },
  balanceText: {
    fontSize: 36,
    fontWeight: 'bold',
    color: Theme.colors.textPrimary,
    fontFamily: 'Courier',
  },
  sectionHeader: {
    marginTop: Theme.spacing.s,
    marginBottom: Theme.spacing.m,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: Theme.colors.textPrimary,
  },
  accountsList: {
    gap: Theme.spacing.s,
    marginBottom: Theme.spacing.l,
  },
  accountItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Theme.colors.backgroundSecondary,
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.m,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
  },
  accountType: {
    color: Theme.colors.textPrimary,
    fontWeight: '600',
    fontSize: 16,
    marginBottom: 4,
  },
  accountNumber: {
    color: Theme.colors.textSecondary,
    fontSize: 12,
    fontFamily: 'Courier',
  },
  accountBalance: {
    color: Theme.colors.textPrimary,
    fontSize: 18,
    fontWeight: 'bold',
    fontFamily: 'Courier',
  },
  transactionsList: {
    backgroundColor: Theme.colors.backgroundGlass,
    borderRadius: Theme.radii.l,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    overflow: 'hidden',
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Theme.spacing.m,
  },
  transactionItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: Theme.colors.glassBorder,
  },
  txLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Theme.spacing.m,
  },
  txIconBox: {
    width: 40,
    height: 40,
    borderRadius: Theme.radii.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  txType: {
    color: Theme.colors.textPrimary,
    fontWeight: '500',
    fontSize: 16,
    marginBottom: 4,
  },
  txRef: {
    color: Theme.colors.textSecondary,
    fontSize: 12,
    fontFamily: 'Courier',
  },
  txAmount: {
    fontWeight: 'bold',
    fontSize: 16,
    fontFamily: 'Courier',
  },
  emptyText: {
    color: Theme.colors.textSecondary,
    textAlign: 'center',
    padding: Theme.spacing.l,
  }
});

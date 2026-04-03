import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { transferFundsApi } from '@/api/client';
import { Theme } from '@/constants/PayFastTheme';
import { Send, CheckCircle2 } from 'lucide-react-native';

export default function TransferScreen() {
  const [toAccountId, setToAccountId] = useState('');
  const [amount, setAmount] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const router = useRouter();

  const handleTransfer = async () => {
    if (!toAccountId || !amount) {
      setError('Destination Account ID and Amount are required.');
      return;
    }

    const amountPaise = parseInt(amount, 10);
    if (isNaN(amountPaise) || amountPaise <= 0) {
      setError('Invalid amount.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await transferFundsApi(toAccountId, amountPaise, notes);
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Transfer failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSuccess(false);
    setToAccountId('');
    setAmount('');
    setNotes('');
  };

  if (success) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <View style={styles.successCard}>
          <View style={styles.successIconBox}>
            <CheckCircle2 size={48} color={Theme.colors.accentSecondary} />
          </View>
          <Text style={styles.successTitle}>Transfer Successful</Text>
          <Text style={styles.successSubtitle}>Your funds have been securely sent.</Text>
          <TouchableOpacity style={styles.primaryButton} onPress={() => router.navigate('/(tabs)')}>
            <Text style={styles.primaryButtonText}>Return to Dashboard</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryButton} onPress={handleReset}>
            <Text style={styles.secondaryButtonText}>Send Another Transfer</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Send Funds</Text>
          <Text style={styles.subtitle}>Execute secure transfers instantly.</Text>
        </View>

        <View style={styles.formPanel}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Destination Account ID</Text>
            <TextInput 
              style={[styles.input, { fontFamily: 'Courier' }]}
              placeholder="UUID format"
              placeholderTextColor={Theme.colors.textTertiary}
              value={toAccountId}
              onChangeText={setToAccountId}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Amount (Paise)</Text>
            <View style={styles.currencyInputContainer}>
              <Text style={styles.currencySymbol}>$</Text>
              <TextInput 
                style={[styles.input, styles.currencyInput]}
                placeholder="1000"
                placeholderTextColor={Theme.colors.textTertiary}
                value={amount}
                onChangeText={setAmount}
                keyboardType="number-pad"
              />
            </View>
            <Text style={styles.helperText}>100 paise = 1 Unit</Text>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Notes (Optional)</Text>
            <TextInput 
              style={styles.input}
              placeholder="e.g. Dinner split"
              placeholderTextColor={Theme.colors.textTertiary}
              value={notes}
              onChangeText={setNotes}
            />
          </View>

          {error ? (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}

          <TouchableOpacity style={styles.primaryButton} onPress={handleTransfer} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <View style={styles.buttonInner}>
                <Text style={styles.primaryButtonText}>Send Money</Text>
                <Send size={18} color="#fff" />
              </View>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Theme.colors.background,
  },
  content: {
    padding: Theme.spacing.l,
  },
  header: {
    marginBottom: Theme.spacing.xl,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Theme.colors.textPrimary,
  },
  subtitle: {
    fontSize: 14,
    color: Theme.colors.textSecondary,
    marginTop: Theme.spacing.s,
  },
  formPanel: {
    backgroundColor: Theme.colors.backgroundGlass,
    padding: Theme.spacing.l,
    borderRadius: Theme.radii.l,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    gap: Theme.spacing.m,
  },
  inputGroup: {
    gap: Theme.spacing.s,
  },
  label: {
    color: Theme.colors.textSecondary,
    fontSize: 14,
  },
  input: {
    backgroundColor: Theme.colors.backgroundSecondary,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    borderRadius: Theme.radii.m,
    color: Theme.colors.textPrimary,
    padding: Theme.spacing.m,
  },
  currencyInputContainer: {
    position: 'relative',
    justifyContent: 'center',
  },
  currencySymbol: {
    position: 'absolute',
    left: 14,
    color: Theme.colors.textTertiary,
    fontSize: 16,
    zIndex: 1,
  },
  currencyInput: {
    paddingLeft: 30,
    fontFamily: 'Courier',
  },
  helperText: {
    fontSize: 12,
    color: Theme.colors.textTertiary,
  },
  errorBox: {
    padding: Theme.spacing.m,
    backgroundColor: 'rgba(255, 51, 102, 0.1)',
    borderLeftWidth: 4,
    borderLeftColor: Theme.colors.accentDanger,
    borderRadius: Theme.radii.s,
  },
  errorText: {
    color: Theme.colors.textPrimary,
    fontSize: 14,
  },
  primaryButton: {
    backgroundColor: Theme.colors.accentPrimary,
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.full,
    alignItems: 'center',
    marginTop: Theme.spacing.s,
  },
  primaryButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  buttonInner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Theme.spacing.s,
  },
  secondaryButton: {
    backgroundColor: Theme.colors.backgroundSecondary,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.full,
    alignItems: 'center',
    marginTop: Theme.spacing.m,
  },
  secondaryButtonText: {
    color: Theme.colors.textPrimary,
    fontWeight: '600',
    fontSize: 16,
  },
  successCard: {
    backgroundColor: Theme.colors.backgroundGlass,
    padding: Theme.spacing.xl,
    borderRadius: Theme.radii.l,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    alignItems: 'center',
    width: '90%',
    maxWidth: 400,
  },
  successIconBox: {
    padding: Theme.spacing.m,
    backgroundColor: 'rgba(0, 255, 187, 0.1)',
    borderRadius: Theme.radii.full,
    marginBottom: Theme.spacing.l,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Theme.colors.textPrimary,
    marginBottom: Theme.spacing.s,
  },
  successSubtitle: {
    fontSize: 14,
    color: Theme.colors.textSecondary,
    marginBottom: Theme.spacing.xl,
    textAlign: 'center',
  }
});

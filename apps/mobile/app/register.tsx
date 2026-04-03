import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { registerApi } from '../api/client';
import { Theme } from '../constants/PayFastTheme';
import { Lock, Phone, User } from 'lucide-react-native';

export default function RegisterScreen() {
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleRegister = async () => {
    if (!phone || !password || !fullName) {
      setError('All fields are required');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      await registerApi(phone, fullName, password);
      router.replace('/(tabs)');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.header}>
          <View style={styles.iconContainer}>
            <User size={32} color={Theme.colors.accentSecondary} />
          </View>
          <Text style={styles.title}>Join PayFast</Text>
          <Text style={styles.subtitle}>The elite core banking platform.</Text>
        </View>

        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Full Name</Text>
            <View style={styles.inputContainer}>
              <User size={18} color={Theme.colors.textTertiary} style={styles.inputIcon} />
              <TextInput 
                style={styles.input}
                placeholder="John Doe"
                placeholderTextColor={Theme.colors.textTertiary}
                value={fullName}
                onChangeText={setFullName}
              />
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Phone Number</Text>
            <View style={styles.inputContainer}>
              <Phone size={18} color={Theme.colors.textTertiary} style={styles.inputIcon} />
              <TextInput 
                style={styles.input}
                placeholder="+1..."
                placeholderTextColor={Theme.colors.textTertiary}
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
              />
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Password</Text>
            <View style={styles.inputContainer}>
              <Lock size={18} color={Theme.colors.textTertiary} style={styles.inputIcon} />
              <TextInput 
                style={styles.input}
                placeholder="••••••••"
                placeholderTextColor={Theme.colors.textTertiary}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
            </View>
          </View>

          {error ? (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}

          <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Create Account</Text>
            )}
          </TouchableOpacity>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => router.replace('/login')}>
              <Text style={styles.linkText}>Sign in</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Theme.colors.background,
    justifyContent: 'center',
    padding: Theme.spacing.l,
  },
  content: {
    backgroundColor: Theme.colors.backgroundGlass,
    borderRadius: Theme.radii.l,
    padding: Theme.spacing.l,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
  },
  header: {
    alignItems: 'center',
    marginBottom: Theme.spacing.xl,
  },
  iconContainer: {
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.full,
    backgroundColor: 'rgba(0, 255, 187, 0.1)',
    marginBottom: Theme.spacing.m,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Theme.colors.textPrimary,
    marginBottom: Theme.spacing.s,
  },
  subtitle: {
    color: Theme.colors.textSecondary,
    fontSize: 14,
  },
  form: {
    gap: Theme.spacing.m,
  },
  inputGroup: {
    gap: Theme.spacing.s,
  },
  label: {
    color: Theme.colors.textSecondary,
    fontSize: 14,
  },
  inputContainer: {
    position: 'relative',
    justifyContent: 'center',
  },
  inputIcon: {
    position: 'absolute',
    left: 12,
    zIndex: 1,
  },
  input: {
    backgroundColor: Theme.colors.backgroundSecondary,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    borderRadius: Theme.radii.m,
    color: Theme.colors.textPrimary,
    padding: Theme.spacing.m,
    paddingLeft: 40,
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
  button: {
    backgroundColor: Theme.colors.accentPrimary,
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.full,
    alignItems: 'center',
    marginTop: Theme.spacing.m,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: Theme.spacing.l,
  },
  footerText: {
    color: Theme.colors.textSecondary,
    fontSize: 14,
  },
  linkText: {
    color: Theme.colors.accentSecondary,
    fontWeight: '500',
    fontSize: 14,
  }
});

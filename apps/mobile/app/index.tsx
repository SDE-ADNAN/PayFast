import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { Theme } from '../constants/PayFastTheme';
import { Zap } from 'lucide-react-native';

export default function LandingScreen() {
  const router = useRouter();
  const [init, setInit] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    SecureStore.getItemAsync('token').then(token => {
      if (token) {
        router.replace('/(tabs)');
      } else {
        setInit(false);
      }
    });
  }, []);

  if (init) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={Theme.colors.accentPrimary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Zap size={48} color={Theme.colors.accentSecondary} />
        </View>
        <Text style={styles.title}>PayFast</Text>
        <Text style={styles.subtitle}>
          High-Performance. Zero Compromises. The elite core banking platform.
        </Text>

        <TouchableOpacity 
          style={styles.primaryButton}
          onPress={() => router.push('/register')}
        >
          <Text style={styles.primaryButtonText}>Get Started</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.secondaryButton}
          onPress={() => router.push('/login')}
        >
          <Text style={styles.secondaryButtonText}>Log In</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Theme.colors.background,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Theme.spacing.xl,
  },
  iconContainer: {
    padding: Theme.spacing.l,
    borderRadius: Theme.radii.full,
    backgroundColor: 'rgba(0, 255, 187, 0.1)',
    marginBottom: Theme.spacing.l,
  },
  title: {
    fontSize: 48,
    fontWeight: '900',
    color: Theme.colors.textPrimary,
    marginBottom: Theme.spacing.m,
  },
  subtitle: {
    fontSize: 16,
    color: Theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: Theme.spacing.xxl,
  },
  primaryButton: {
    backgroundColor: Theme.colors.accentPrimary,
    width: '100%',
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.full,
    alignItems: 'center',
    marginBottom: Theme.spacing.m,
    shadowColor: Theme.colors.accentPrimary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: Theme.colors.backgroundSecondary,
    borderWidth: 1,
    borderColor: Theme.colors.glassBorder,
    width: '100%',
    padding: Theme.spacing.m,
    borderRadius: Theme.radii.full,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: Theme.colors.textPrimary,
    fontSize: 18,
    fontWeight: '600',
  }
});

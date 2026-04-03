import { Tabs } from 'expo-router';
import React from 'react';
import { Platform } from 'react-native';

import { Theme } from '@/constants/PayFastTheme';
import { Home, ArrowLeftRight } from 'lucide-react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Theme.colors.accentSecondary,
        headerShown: false,
        tabBarStyle: Platform.select({
          default: {
            backgroundColor: Theme.colors.backgroundSecondary,
            borderTopWidth: 1,
            borderTopColor: Theme.colors.glassBorder,
          },
        }),
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color }) => <Home size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="transfer" // we will create app/(tabs)/transfer.tsx later for MVP flow
        options={{
          title: 'Transfer',
          tabBarIcon: ({ color }) => <ArrowLeftRight size={28} color={color} />,
        }}
      />
    </Tabs>
  );
}

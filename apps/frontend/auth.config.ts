import { NextAuthConfig } from 'next-auth';
import CredentialProvider from 'next-auth/providers/credentials';
import GithubProvider from 'next-auth/providers/github';

const authConfig = {
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_ID ?? '',
      clientSecret: process.env.GITHUB_SECRET ?? ''
    }),
  ],
  pages: {
    signIn: '/' //sigin page
  },
  callbacks: {
    async signIn({ user, account, profile }) {
      // Check if the user is signing in with GitHub
      if (account?.provider === 'github') {
        try {
          // Make a request to your FastAPI backend to store the user
          const response = await fetch('http://your-fastapi-backend.com/register/github', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: profile.login,
              email: profile.email || user.email,
              // Include any other necessary user data
            }),
          });

          if (response.ok) {
            // User registered successfully
            return true;
          } else {
            // Handle registration error
            return false;
          }
        } catch (error) {
          console.error('Error registering user:', error);
          return false;
        }
      }

      // If the user is signing in with Credentials provider
      // (or any other provider you have)
      // Implement your logic to store the user in the database

      return true; // Allow the sign-in process to continue
    },
  },
} satisfies NextAuthConfig;

export default authConfig;

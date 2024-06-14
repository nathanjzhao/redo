import { NextAuthConfig } from 'next-auth';
import CredentialProvider from 'next-auth/providers/credentials';
import GithubProvider from 'next-auth/providers/github';

const authConfig = {
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_ID ?? '',
      clientSecret: process.env.GITHUB_SECRET ?? '',
      redirectUri: `${process.env.NEXTAUTH_URL}/api/auth/callback/github`
      // Set Github Authorization callback URL to http://localhost:3000/api/auth/callback/github
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
          console.log("user", user);
          console.log("account", account);
          console.log("profile", profile);
          const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register/github`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: profile.login,
              email: profile.email || user.email,
              name: profile.name | user.name,
              image: profile.image || user.image,
              github_id: profile.node_id,
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
    // The `session` calback defines JWT tokens to be used in session
    async session({ session, token, user }) {
      session.userId = token.id;
      session.accessToken = token.accessToken;
      session.nodeId = token.node_id;
      return session;
    },
    async jwt({ token, user, account, profile, isNewUser }) {
      if (user) {
        token.id = user.id;
      }
      if (account) {
        token.accessToken = account.access_token;
      }
      if (profile) {
        token.node_id = profile.node_id;
      }
      return token;
    },
  },
} satisfies NextAuthConfig;

export default authConfig;

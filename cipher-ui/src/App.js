import React, { useEffect, useState } from 'react';
import {
  ChakraProvider,
  Box,
  Heading,
  Text,
  Stack,
  Container,
  Button,
} from '@chakra-ui/react';
import axios from 'axios';
import yaml from 'yaml';
import Login from './Login';

function App() {
  const [encryptedMessages, setEncryptedMessages] = useState({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userId, setUserId] = useState('');

  useEffect(() => {
    if (isLoggedIn) {
      axios.get('./encrypted_messages.yaml')
        .then((response) => {
          const parsedData = yaml.parse(response.data);
          setEncryptedMessages(parsedData);
        })
        .catch((error) => {
          console.error('Error fetching YAML file:', error);
        });
    }
  }, [isLoggedIn]);

  const handleLogin = (loginUserId) => {
    setIsLoggedIn(true);
    setUserId(loginUserId);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserId('');
    setEncryptedMessages({});
  };

  return (
    <ChakraProvider>
      <Container maxW="container.lg" p={4}>
        <Heading as="h1" size="xl" mb={4}>
          Encrypted Messages
        </Heading>
        {!isLoggedIn ? (
          <Login onLogin={handleLogin} />
        ) : (
          <>
            <Button onClick={handleLogout} mb={4}>Logout</Button>
            {encryptedMessages[userId] ? (
              <Stack spacing={4}>
                <Box p={4} shadow="md" borderWidth="1px">
                  <Heading as="h2" size="md" mb={2}>
                    User ID: {userId}
                  </Heading>
                  {encryptedMessages[userId].map((message, index) => (
                    <Box key={index} p={2}>
                      <Text><strong>Original:</strong> {message.message}</Text>
                      <Text><strong>Encrypted:</strong> {message.encrypted}</Text>
                      <Text><strong>Key:</strong> {message.key}</Text>
                    </Box>
                  ))}
                </Box>
              </Stack>
            ) : (
              <Text>No encrypted messages found for this user.</Text>
            )}
          </>
        )}
      </Container>
    </ChakraProvider>
  );
}

export default App;
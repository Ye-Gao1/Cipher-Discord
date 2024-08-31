import React, { useEffect, useState } from 'react';
import {
  ChakraProvider,
  Box,
  Heading,
  Text,
  Stack,
  Container,
} from '@chakra-ui/react';
import axios from 'axios';
import yaml from 'yaml';

function App() {
  const [encryptedMessages, setEncryptedMessages] = useState({});

  useEffect(() => {
    axios.get('./encrypted_messages.yaml')
      .then((response) => {
        const parsedData = yaml.parse(response.data);
        setEncryptedMessages(parsedData);
      })
      .catch((error) => {
        console.error('Error fetching YAML file:', error);
      });
  }, []);

  return (
    <ChakraProvider>
      <Container maxW="container.lg" p={4}>
        <Heading as="h1" size="xl" mb={4}>
          Encrypted Messages
        </Heading>
        {Object.keys(encryptedMessages).length === 0 ? (
          <Text>No encrypted messages found.</Text>
        ) : (
          <Stack spacing={4}>
            {Object.entries(encryptedMessages).map(([userId, messages]) => (
              <Box key={userId} p={4} shadow="md" borderWidth="1px">
                <Heading as="h2" size="md" mb={2}>
                  User ID: {userId}
                </Heading>
                {messages.map((message, index) => (
                  <Box key={index} p={2}>
                    <Text><strong>Original:</strong> {message.message}</Text>
                    <Text><strong>Encrypted:</strong> {message.encrypted}</Text>
                    <Text><strong>Key:</strong> {message.key}</Text>
                  </Box>
                ))}
              </Box>
            ))}
          </Stack>
        )}
      </Container>
    </ChakraProvider>
  );
}

export default App;

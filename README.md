# UNO_grade11th_final_project

this is a UNO game, this project is for my 11th grade final, the game is a multiplayer game where \

every client can create or join rooms and play uno.



## PROTOCOL DOCUMENT:



### protocols:

#### 1. RSA public Key Request (`RSA`)
* **Direction**: Client to Server
* **Format**: `RSA`
* **Description**: sends a request to the server for the public RSA key

#### 2. Public Key Response (`PUBKEY`)
* **Direction**: Server to Client
* **Format**: `PUBKEY|<rsa_public_key>`
* **Description**: The server sends its public key encoded in Base64. 

#### 3. Key Exchange (`KEY`)
* **Direction**: Client tp Server
* **Format**: `KEY|<aes_key>`
* **Description**: the client sends the AES key that the communication will use

#### 4. Key Exchange Acknowledgment (`RKEY`)
* **Direction**: Server to Client
* **Format**: `RKEY`
* **Description**: a confirmation by the server that he got the AES key


#### 5. Sign Up Request (`SGN`)
* **Direction**: Client to Server
* **Format**: `SGN|<username>|<password>|<name>|<email>`
* **Description**: sends a request to sign in

#### 6. Sign Up Response (`RSGN`)
* **Direction**: Server to Client
* **Format**: `RSGN|<status_message>`
* **Description**: Returns `"username already exists"` if the user already exists, or a generic confirmation

#### 7. Login Request (`LGN`)
* **Direction**: Client to Server
* **Format**: `LGN|<username>|<password>`
* **Description**: the client trying to log it

#### 8. Login Response (`RLGN`)
* **Direction**: Server $\rightarrow$ Client
* **Format**: `RLGN|<status_message>|<username>|<password>`
* **Description**:  returns `"Login successful"` if the client is logged it. or an Error like: `"User does not exist"`, `"Wrong password"`, or `"user already logged in"`.

#### 9. Email Reset Password Request (`ERP`)
* **Direction**: Client to Server
* **Format**: `ERP|<email>`
* **Description**: request an email for password reset

#### 10. Email Reset Password Response (`ERPR`)
* **Direction**: Server to Client
* **Format**: `ERPR|<status_message>|<email>`
* **Description**: sends an email with a reset code, and (`"got Reset Code"`) or (`"email does not exist"`) if no such email exists.

#### 11. Get Reset Code verification (`GRP`)
* **Direction**: Client to Server
* **Format**: `GRP|<verification_code>`
* **Description**: sends the 6 number verification code

#### 12. Get Reset Code Response (`GRPR`)
* **Direction**: Server to Client
* **Format**: `GRPR|<status_message>`
* **Description**: verifies the code, sends (`"code received"`) if the code was correct, if the code fails it sends: (`"wrong code, try again"`), or (`"code expired"`) if the time expired.

#### 13. Reset New Password (`RNP`)
* **Direction**: Client to Server
* **Format**: `RNP|<new_password>|<verified_email>`
* **Description**: client sends the new password

#### 14. Reset Password Response (`RRMP`)
* **Direction**: Server to Client
* **Format**: `RRMP|reset password`
* **Description**: reset the password in the database and sends confirmation to client

#### 15. Create Room Request (`CRR`)
* **Direction**: Client to Server
* **Format**: `CRR|<host_username>`
* **Description**: Client sending request to create a room

#### 16. Create Room Response (`RCRR`)
* **Direction**: Server to Client
* **Format**: `RCRR|room created|<players_dictionary>`
* **Description**: Creates a new room, and sends to the client the room's player data: `{"player_name": player_id}`.

#### 17. Fetch Active Rooms List (`ROOMS`)
* **Direction**: Client to Server
* **Format**: `ROOMS`
* **Description**: a request for all the rooms that exists now 

#### 18. Rooms List Response (`ROOML`)
* **Direction**: Server to Client
* **Format**: `ROOML|<room_list_dictionary>`
* **Description**: returns a dict with all the rooms and the player count: `{"[Host Name]'s room": player_count}`.

#### 19. Join Existing Room Request (`JOIN`)
* **Direction**: Client to Server
* **Format**: `JOIN|<target_room_name>`
* **Description**: client request to join an already existing room

#### 20. Join Room Response (`RJOI`)
* **Direction**: Server to Client
* **Format**: `RJOI|<room_name>|<players_dictionary>`
* **Description**: server confirmation to client that he joined the room, and add him to the room

#### 21. Realtime Room Joins (`NEW`)
* **Direction**: Server to Client 
* **Format**: `NEW|<new_player_username>|<new_player_id>`
* **Description**: sends to every existing client in the room that a new player has joined

#### 22. Leave Room Request (`DEL`)
* **Direction**: Client to Server 
* **Format**: `DEL|<leaving_username>`
* **Description**: deletes a player from game. *Note: If a player was the host, `clear_room()` is called to close down the room.*

#### 23. Realtime Room Leaves (`DELP`)
* **Direction**: Server to Client 
* **Format**: `DELP|<disconnected_username>`
* **Description**: sends to every client that a player has left

#### 24. Start Game Request (`STR`)
* **Direction**: Client to Server
* **Format**: `STR`
* **Description**: request to start the game

#### 25. Game Initialization Broadcast (`RSTR`)
* **Direction**: Server to Client 
* **Format**: `RSTR|the game has started`
* **Description**: sends to every client that the game has started

#### 26. Player Hand State Synch (`CARDS`)
* **Direction**: Server to Client
* **Format**: `CARDS|<list_of_tuples>`
* **Description**: sends to every player the cards in there hand`.

#### 27. Pile State Sync (`CPLY`)
* **Direction**: Server to Client 
* **Format**: `CPLY|the new card is|<tuple_representation>`
* **Description**: sends to every client what is the new card.

#### 28. Turn Enforcement Activation (`TURN`)
* **Direction**: Server to Client
* **Format**: `TURN`
* **Description**: sends to a client that this is their turn

#### 29. Intercept Input Locking (`STOP`)
* **Direction**: Server to Client 
* **Format**: `STOP`
* **Description**: sends to a client that this is not their turn and they shell not play

#### 30. Draw Deck Card Request (`ADD`)
* **Direction**: Client to Server
* **Format**: `ADD`
* **Description**: a player request to draw a card, adds a random card to the players hand

#### 31. Card Discard Play Submission (`PLAY`)
* **Direction**: Client to Server
* **Format**: `PLAY|<card_tuple_string>`
* **Description**: client submits what card he just played.

#### 32. Wild Card Color Request (`CHANGE`)
* **Direction**: Server to Client
* **Format**: `CHANGE`
* **Description**: asks the client what color he wants to change the current color to

#### 33. Wild Card Color Choice Execution (`CHAN`)
* **Direction**: Client to Server
* **Format**: `CHAN|<selected_color>`
* **Description**: the client sends the color they have chosen the change the color to.

#### 34. Player Hand Size Totals Update (`PCOUNT`)
* **Direction**: Server to Client 
* **Format**: `PCOUNT|<dictionary>`
* **Description**: sends to every client what is the number of cards the other players have

#### 35. Uno Callout (`UNO`)
* **Direction**: Server to Client 
* **Format**: `UNO|<username>`
* **Description**: sends that one user has 1 card remaining

#### 36. Winner Announcement (`WIN`)
* **Direction**: Server to Client 
* **Format**: `WIN|<winning_username>`
* **Description**: announces the winning player and ends the game

#### 37. Lobby Population Failure (`NOP`)
* **Direction**: Server to Client
* **Format**: `NOP`
* **Description**: send to the host `"Not enough player"` if he is the only player in the room.

#### 38. General Exception Flag (`ERR`)
* **Direction**: Server to Client
* **Format**: `ERR|<error_reason_string>`
* **Description**: a Generic error
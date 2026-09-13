package com.example.demo.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;

import com.example.demo.dao.UserRepo;
import com.example.demo.model.TopscoreWrapper;
import com.example.demo.model.User;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepo userRepo;

    private UserService userService;

    @BeforeEach
    void setUp() {
        userService = new UserService();
        ReflectionTestUtils.setField(userService, "userrepo", userRepo);
    }

    @Test
    void adduser_shouldRejectExistingUsername() {
        User user = new User();
        user.setUsername("alice");
        user.setPassword("secret");
        when(userRepo.findByUsername("alice")).thenReturn(user);

        ResponseEntity<String> result = userService.adduser(user);

        assertEquals(HttpStatus.BAD_REQUEST, result.getStatusCode());
        assertEquals("Username already exists.", result.getBody());
    }

    @Test
    void adduser_shouldCreateUserWhenUsernameIsNew() {
        User user = new User();
        user.setUsername("bob");
        user.setPassword("secret");
        when(userRepo.findByUsername("bob")).thenReturn(null);

        ResponseEntity<String> result = userService.adduser(user);

        assertEquals(HttpStatus.CREATED, result.getStatusCode());
        assertEquals("user created", result.getBody());
        assertEquals(0, user.getHighscore());
        verify(userRepo).save(user);
    }

    @Test
    void login_shouldSucceedWithMatchingCredentials() {
        User user = new User();
        user.setUsername("alice");
        user.setPassword("secret");
        when(userRepo.findByUsername("alice")).thenReturn(user);

        ResponseEntity<String> result = userService.login(user);

        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals("login successfull", result.getBody());
    }

    @Test
    void login_shouldFailWithInvalidCredentials() {
        User user = new User();
        user.setUsername("alice");
        user.setPassword("wrong");
        User dbUser = new User();
        dbUser.setUsername("alice");
        dbUser.setPassword("secret");
        when(userRepo.findByUsername("alice")).thenReturn(dbUser);

        ResponseEntity<String> result = userService.login(user);

        assertEquals(HttpStatus.UNAUTHORIZED, result.getStatusCode());
        assertEquals("invalid credentials", result.getBody());
    }

    @Test
    void updatescore_shouldReturnNotFoundWhenUserDoesNotExist() {
        when(userRepo.findByUsername("missing")).thenReturn(null);

        ResponseEntity<String> result = userService.updatescore("missing", 100);

        assertEquals(HttpStatus.NOT_FOUND, result.getStatusCode());
        assertEquals("user not exist", result.getBody());
    }

    @Test
    void updatescore_shouldSaveNewHighscore() {
        User user = new User();
        user.setUsername("alice");
        user.setHighscore(100);
        when(userRepo.findByUsername("alice")).thenReturn(user);

        ResponseEntity<String> result = userService.updatescore("alice", 250);

        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals("score updated", result.getBody());
        assertEquals(250, user.getHighscore());
        verify(userRepo).save(user);
    }

    @Test
    void updatescore_shouldNotSaveWhenNewScoreIsLower() {
        User user = new User();
        user.setUsername("alice");
        user.setHighscore(250);
        when(userRepo.findByUsername("alice")).thenReturn(user);

        ResponseEntity<String> result = userService.updatescore("alice", 200);

        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals("score updated", result.getBody());
        assertEquals(250, user.getHighscore());
    }

    @Test
    void getTopscorers_shouldReturnTopPlayers() {
        List<Integer> scores = List.of(500, 300);
        TopscoreWrapper first = new TopscoreWrapper("alice", 500);
        TopscoreWrapper second = new TopscoreWrapper("bob", 300);
        when(userRepo.getTopscores(2)).thenReturn(scores);
        when(userRepo.getUsersWithScores(scores)).thenReturn(List.of(first, second));

        ResponseEntity<List<TopscoreWrapper>> result = userService.getTopscorers();

        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals(2, result.getBody().size());
        assertEquals("alice", result.getBody().get(0).getUsername());
        verify(userRepo).getTopscores(2);
        verify(userRepo).getUsersWithScores(scores);
    }
}

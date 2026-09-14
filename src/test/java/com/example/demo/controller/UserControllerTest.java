package com.example.demo.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import com.example.demo.model.TopscoreWrapper;
import com.example.demo.model.User;
import com.example.demo.service.UserService;

@ExtendWith(MockitoExtension.class)
class UserControllerTest {

    @Mock
    private UserService userService;

    @InjectMocks
    private UserController userController;

    @Test
    void adduser_shouldReturnResponseFromService() {
        User user = new User();
        user.setUsername("alice");
        ResponseEntity<String> expected = ResponseEntity.status(HttpStatus.CREATED).body("user created");
        when(userService.adduser(user)).thenReturn(expected);

        ResponseEntity<String> result = userController.adduser(user);

        assertEquals(expected, result);
        verify(userService).adduser(user);
    }

    @Test
    void login_shouldReturnResponseFromService() {
        User user = new User();
        user.setUsername("alice");
        ResponseEntity<String> expected = ResponseEntity.ok("login successfull");
        when(userService.login(user)).thenReturn(expected);

        ResponseEntity<String> result = userController.login(user);

        assertEquals(expected, result);
        verify(userService).login(user);
    }

    @Test
    void updatescore_shouldReturnResponseFromService() {
        ResponseEntity<String> expected = ResponseEntity.ok("score updated");
        when(userService.updatescore("alice", 450)).thenReturn(expected);

        ResponseEntity<String> result = userController.updatescore("alice", 450);

        assertEquals(expected, result);
        verify(userService).updatescore("alice", 450);
    }

    @Test
    void getTopscorers_shouldReturnResponseFromService() {
        TopscoreWrapper top = new TopscoreWrapper("alice", 500);
        List<TopscoreWrapper> topScores = List.of(top);
        ResponseEntity<List<TopscoreWrapper>> expected = ResponseEntity.ok(topScores);
        when(userService.getTopscorers()).thenReturn(expected);

        ResponseEntity<List<TopscoreWrapper>> result = userController.getTopscorers();

        assertEquals(expected, result);
        verify(userService).getTopscorers();
    }

    @Test
    void getSecondTopScorer_shouldReturnResponseFromService() {
        TopscoreWrapper second = new TopscoreWrapper("bob", 300);
        List<TopscoreWrapper> secondScores = List.of(second);
        ResponseEntity<List<TopscoreWrapper>> expected = ResponseEntity.ok(secondScores);
        when(userService.getSecondTopScorer()).thenReturn(expected);

        ResponseEntity<List<TopscoreWrapper>> result = userController.getSecondTopScorer();

        assertEquals(expected, result);
        verify(userService).getSecondTopScorer();
    }
}

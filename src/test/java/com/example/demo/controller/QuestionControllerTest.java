package com.example.demo.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;

import com.example.demo.model.Question;
import com.example.demo.service.QuestionService;

@ExtendWith(MockitoExtension.class)
class QuestionControllerTest {

    @Mock
    private QuestionService questionService;

    @InjectMocks
    private QuestionController questionController;

    @Test
    void addques_shouldReturnSavedQuestion() {
        Question question = new Question();
        question.setId(1);
        question.setCategory("history");

        when(questionService.addques(question)).thenReturn(question);

        Question result = questionController.addques(question);

        assertSame(question, result);
        verify(questionService).addques(question);
    }

    @Test
    void delques_shouldReturnDeleteMessage() {
        when(questionService.delques(7)).thenReturn("deleted7");

        String result = questionController.delques(7);

        assertEquals("deleted7", result);
        verify(questionService).delques(7);
    }

    @Test
    void delquesmul_shouldReturnDeleteMessage() {
        List<Integer> ids = List.of(1, 2, 3);
        when(questionService.delquesmul(ids)).thenReturn("deleted[1, 2, 3]");

        String result = questionController.delquesmul(ids);

        assertEquals("deleted[1, 2, 3]", result);
        verify(questionService).delquesmul(ids);
    }

    @Test
    void delquesall_shouldReturnDeleteAllMessage() {
        when(questionService.delquesall()).thenReturn("all deleted");

        String result = questionController.delquesmul();

        assertEquals("all deleted", result);
        verify(questionService).delquesall();
    }

    @Test
    void getquesall_shouldReturnResponseFromService() {
        List<Question> questions = List.of(new Question());
        List<Question> expected = questions;
        when(questionService.getquesall()).thenReturn(expected);

        ResponseEntity<List<Question>> result = questionController.getquesall();

        assertEquals(expected, result);
        verify(questionService).getquesall();
    }

    @Test
    void getquesByCategory_shouldReturnQuestions() {
        List<Question> questions = List.of(new Question());
        when(questionService.getquesByCategory("history")).thenReturn(questions);

        List<Question> result = questionController.getquesByCategory("history");

        assertEquals(questions, result);
        verify(questionService).getquesByCategory("history");
    }

    @Test
    void getquesByCategoryAndCount_shouldReturnQuestions() {
        List<Question> questions = List.of(new Question());
        when(questionService.getquesByCategoryAndCount("history", 2)).thenReturn(questions);

        List<Question> result = questionController.getquesByCategoryAndCount("history", 2);

        assertEquals(questions, result);
        verify(questionService).getquesByCategoryAndCount("history", 2);
    }
}

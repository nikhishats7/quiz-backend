package com.example.demo.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.ArrayList;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;

import com.example.demo.dao.QuestionRepo;
import com.example.demo.model.Question;

@ExtendWith(MockitoExtension.class)
class QuestionServiceTest {

    @Mock
    private QuestionRepo questionRepo;

    private QuestionService questionService;

    @BeforeEach
    void setUp() {
        questionService = new QuestionService();
        ReflectionTestUtils.setField(questionService, "qrepo", questionRepo);
    }

    @Test
    void addques_shouldSaveAndReturnQuestion() {
        Question question = new Question();
        question.setCategory("history");
        question.setQuesTitle("Who discovered India?");

        when(questionRepo.save(question)).thenReturn(question);

        Question result = questionService.addques(question);

        assertEquals(question, result);
        verify(questionRepo).save(question);
    }

    @Test
    void delques_shouldDeleteAndReturnMessage() {
        String result = questionService.delques(12);

        assertEquals("deleted12", result);
        verify(questionRepo).deleteById(12);
    }

    @Test
    void delquesmul_shouldDeleteAllAndReturnMessage() {
        List<Integer> ids = List.of(1, 2, 3);

        String result = questionService.delquesmul(ids);

        assertEquals("deleted[1, 2, 3]", result);
        verify(questionRepo).deleteAllById(ids);
    }

    @Test
    void delquesall_shouldDeleteAllAndReturnMessage() {
        String result = questionService.delquesall();

        assertEquals("all deleted", result);
        verify(questionRepo).deleteAll();
    }

    @Test
    void getquesall_shouldReturnOkResponseWhenRepoReturnsQuestions() {
        List<Question> questions = List.of(new Question());
        when(questionRepo.findAll()).thenReturn(questions);

        List<Question> result = questionService.getquesall();

        assertEquals(questions, result);
        verify(questionRepo).findAll();
    }

    @Test
    void getquesall_shouldReturnBadRequestOnException() {
        when(questionRepo.findAll()).thenThrow(new RuntimeException("db down"));

       List<Question> result = questionService.getquesall();

        assertEquals(new ArrayList<>(), result);
    }

    @Test
    void getquesByCategory_shouldReturnQuestions() {
        List<Question> questions = List.of(new Question());
        when(questionRepo.getByCategory("history")).thenReturn(questions);

        List<Question> result = questionService.getquesByCategory("history");

        assertEquals(questions, result);
        verify(questionRepo).getByCategory("history");
    }

    @Test
    void getquesByCategoryAndCount_shouldReturnRandomQuestions() {
        List<Question> questions = List.of(new Question(), new Question());
        when(questionRepo.getRandomQuestionByCategory("history", 2)).thenReturn(questions);

        List<Question> result = questionService.getquesByCategoryAndCount("history", 2);

        assertEquals(questions, result);
        verify(questionRepo).getRandomQuestionByCategory("history", 2);
    }
}

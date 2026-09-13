package com.example.demo.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.example.demo.dao.QuestionRepo;
import com.example.demo.model.Question;

@ExtendWith(MockitoExtension.class)
public class QuestionServiceTest {

    @Mock
    private QuestionRepo questionRepo;

    @InjectMocks
    private QuestionService questionService;

    @Test
    public void testGetQuesByDiffLevelSuccess() {
        Question q = new Question();
        q.setId(1);
        q.setDiffLevel(2);
        when(questionRepo.findByDiffLevel(2)).thenReturn(Arrays.asList(q));

        List<Question> result = questionService.getquesByDiffLevel(2);
        assertEquals(1, result.size());
        assertEquals(2, result.get(0).getDiffLevel());
    }

    @Test
    public void testGetQuesByDiffLevelNotFound() {
        when(questionRepo.findByDiffLevel(99)).thenReturn(Collections.emptyList());

        List<Question> result = questionService.getquesByDiffLevel(99);
        assertEquals(0, result.size());
    }

    @Test
    public void testGetQuesByDiffLevelNull() {
        List<Question> result = questionService.getquesByDiffLevel(null);
        assertEquals(0, result.size());
    }
}

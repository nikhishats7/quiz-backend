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
    public void testGetquesByDiffLevel_Success() {
        Question q = new Question();
        q.setId(1);
        q.setDiffLevel("Easy");
        when(questionRepo.findByDiffLevel("Easy")).thenReturn(Arrays.asList(q));

        List<Question> result = questionService.getquesByDiffLevel("Easy");
        assertEquals(1, result.size());
        assertEquals("Easy", result.get(0).getDiffLevel());
    }

    @Test
    public void testGetquesByDiffLevel_NotFound() {
        when(questionRepo.findByDiffLevel("NonExistent")).thenReturn(Collections.emptyList());

        List<Question> result = questionService.getquesByDiffLevel("NonExistent");
        assertEquals(0, result.size());
    }

    @Test
    public void testGetquesByDiffLevel_Null() {
        List<Question> result = questionService.getquesByDiffLevel(null);
        assertEquals(0, result.size());
    }
}

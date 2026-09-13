package com.example.demo.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
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
	public void testGetquesByDiffLevel() {
		Question q = new Question();
		q.setId(1);
		q.setDiffLevel("Medium");

		when(questionRepo.findByDiffLevel("Medium")).thenReturn(Arrays.asList(q));

		List<Question> result = questionService.getquesByDiffLevel("Medium");
		assertEquals(1, result.size());
		assertEquals("Medium", result.get(0).getDiffLevel());
	}

	@Test
	public void testGetquesByDiffLevelNullOrEmpty() {
		List<Question> resultNull = questionService.getquesByDiffLevel(null);
		assertTrue(resultNull.isEmpty());

		when(questionRepo.findByDiffLevel("NonExistent")).thenReturn(Collections.emptyList());
		List<Question> resultEmpty = questionService.getquesByDiffLevel("NonExistent");
		assertTrue(resultEmpty.isEmpty());
	}
}

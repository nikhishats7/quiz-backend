package com.example.demo.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import java.util.Arrays;
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
		Question q1 = new Question();
		q1.setId(1);
		q1.setDiffLevel(2);

		when(questionRepo.findByDiffLevel(2)).thenReturn(Arrays.asList(q1));

		List<Question> result = questionService.getquesByDiffLevel(2);
		equals(1, result.size());
		equals(2, result.get(0).getDiffLevel());
	}
}

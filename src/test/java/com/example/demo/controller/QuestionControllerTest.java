package com.example.demo.controller;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

import java.util.Arrays;
import java.util.Collections;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import com.example.demo.model.Question;
import com.example.demo.service.QuestionService;

@WebMvcTest(QuestionController.class)
public class QuestionControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@MockBean
	private QuestionService questionService;

	@Test
	public void testGetQuesByDiffLevel() throws Exception {
		Question q = new Question();
		q.setId(1);
		q.setDiffLevel("Easy");

		when(questionService.getquesByDiffLevel("Easy")).thenReturn(Arrays.asList(q));

		mockMvc.perform(get("/getquesByDiffLevel/Easy"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$[0].id").value(1))
				.andExpect(jsonPath("$[0].diffLevel").value("Easy"));
	}

	@Test
	public void testGetQuesByDiffLevelNotFound() throws Exception {
		when(questionService.getquesByDiffLevel("Unknown")).thenReturn(Collections.emptyList());

		mockMvc.perform(get("/getquesByDiffLevel/Unknown"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$").isEmpty());
	}
}

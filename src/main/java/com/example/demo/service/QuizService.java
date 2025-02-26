//package com.example.demo.service;
//
//import java.util.ArrayList;
//import java.util.List;
//import java.util.Optional;
//
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.http.HttpStatus;
//import org.springframework.http.ResponseEntity;
//import org.springframework.stereotype.Service;
//
//import com.example.demo.dao.QuestionRepo;
//import com.example.demo.dao.QuizRepo;
//import com.example.demo.model.Question;
//import com.example.demo.model.QuestionWrapper;
//import com.example.demo.model.Quiz;
//import com.example.demo.model.answerFromUser;
//
//@Service
//public class QuizService {
//	
//	@Autowired
//	QuizRepo quizrepo;
//	
//	@Autowired
//	QuestionRepo quesrepo;
//
//	public String createquiz(String category, Integer qnum, String title) {
//		List<Question> questions= quesrepo.getRandomQuestionByCategory(category, qnum);
//		
//		Quiz quiz = new Quiz();
//		quiz.setTitle(title);
//		quiz.setQuestions(questions);
//		quizrepo.save(quiz);
//		return "quiz created";
//		
//	}
//
//	public ResponseEntity<List<QuestionWrapper>> getquiz(Integer id) {
//		Optional<Quiz> quiz = quizrepo.findById(id);
//		List<Question> questionsOfQuiz = quiz.get().getQuestions(); //as quiz is optional
//		List<QuestionWrapper> questionsWithoutAns = new ArrayList<>();
//		for(Question q : questionsOfQuiz)
//		{
//			QuestionWrapper qnew = new QuestionWrapper(q.getId(),q.getDiffLevel(),
//					q.getCategory(),q.getQuesTitle(),q.getOpt1(),q.getOpt2(),q.getOpt3());
//			questionsWithoutAns.add(qnew);
//		}
//		 
//		return new ResponseEntity<>(questionsWithoutAns, HttpStatus.OK);
//	}
//
//	public ResponseEntity<Integer> getresultOfQuiz(Integer id, List<answerFromUser> answerFromUsers) {
//		Optional<Quiz> quiz = quizrepo.findById(id);
//		List<Question> questionsOfQuiz = quiz.get().getQuestions(); //as quiz is optional
//		int correct = 0;int i = 0;
//		for(answerFromUser r : answerFromUsers)
//		{
//			if(r.getResponse().equals(questionsOfQuiz.get(i).getCorrect()))
//			{
//				correct=correct+1;
//			}
//			i++;
//		}
//		return new ResponseEntity<>(correct,HttpStatus.OK);
//	}
//
//}
